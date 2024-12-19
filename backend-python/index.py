# Comments GPT-ed, but hey, it does a decent job of explaining our unrecognizable code so why not
import csv
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from csv_utils import load_latest_id, load_latest_doc_id, save_processed_docs, load_processed_entries
from lexicon_utils import load_lexicon, preprocess_word, save_words_to_lexicon
from forward_index import save_forward_index
from inverted_index import update_inverted_barrel, create_offsets
from config import forward_index_folder, inverted_index_folder
import re
import ast
import os


# Barrel size determines how many documents each forward index file contains (arbitrary)
barrel_size = 1001

# Function to process and iteratively index a dataset
def iterate_dataset(dataset_file, lexicon_file):
    # Load necessary resources: stop words, processed entries, and the lexicon
    stop_words = set(stopwords.words('english'))
    processed_set = load_processed_entries()
    lexicon = load_lexicon(lexicon_file)
    latest_doc_id = load_latest_doc_id()
    latest_id = load_latest_id()
    
    # Open the dataset file for reading
    with open(dataset_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        forward_entries = []
        lexicon_entries = []
        
        for row in csv_reader:
            # Check if the current document has already been processed
            current_entry = (row['title'], row['url'], row['authors'], row['timestamp'], row['tags'])
            if current_entry in processed_set:
                continue  # Skip already processed entries
            
            # Index the current dataset row and update IDs
            latest_id, latest_doc_id = index_dataset(row, stop_words, latest_doc_id, latest_id, lexicon, lexicon_entries, forward_entries)

            # Mark the document as processed and save it
            processed_set.add(current_entry)
            save_processed_docs([[latest_doc_id, row['title'], row['url'], row['authors'], row['timestamp'], row['tags']]], latest_doc_id)
            
            # Write batches of data to disk after every `barrel_size` documents
            if latest_doc_id % barrel_size == 0:
                save_words_to_lexicon(lexicon, lexicon_entries, latest_id)
                save_forward_index(forward_entries, forward_index_folder)
                lexicon_entries.clear()
                forward_entries.clear()
                print(f"Writing batch {latest_doc_id - barrel_size} to {latest_doc_id}...")
        
        # Save any remaining data after processing all rows
        if forward_entries:
            save_words_to_lexicon(lexicon, lexicon_entries, latest_id)
            save_forward_index(forward_entries, forward_index_folder)
            print(f"Writing batch {latest_doc_id - (latest_doc_id % barrel_size)} to {latest_doc_id}...")


# Processing the tokens to encode their source and position in the articles
def process_tokens(current_position, tokens, combined_tokens, sources, positions, type):
    combined_tokens.extend(tokens)
    sources.extend([type] * len(tokens))
    positions.extend(list(range(current_position, current_position + len(tokens))))
    return current_position + len(tokens)


# Function to index a single dataset row
def index_dataset(row, stop_words, latest_doc_id, latest_id, lexicon, lexicon_entries, forward_entries):
    pattern = r'[^A-Za-z0-9 ]+'
    combined_tokens = []
    
    # Process the title field: tokenize, clean, and filter stop words
    title_tokens = [preprocess_word(token) for token in word_tokenize(re.sub(pattern, ' ', row['title']))]
    title_tokens = [w for w in title_tokens if w.lower() not in stop_words and len(w) > 2]

    # Process the text field: tokenize each paragraph, clean, and filter stop words
    text_tokens = []
    for paragraph in row['text'].split("\n"):
        for token in word_tokenize(re.sub(pattern, ' ', paragraph)):
            text_tokens.append(preprocess_word(token))
    text_tokens = [w for w in text_tokens if w.lower() not in stop_words and len(w) > 2]
    
    # Handle potential errors in tags and authors fields (json.loads would've been better)
    tags_tokens = []
    authors_tokens = []
    try:
        tags_tokens = [preprocess_word(token) for tag in ast.literal_eval(row['tags']) for token in word_tokenize(re.sub(pattern, ' ', tag))]
        authors_tokens = [preprocess_word(token) for author in ast.literal_eval(row['authors']) for token in word_tokenize(re.sub(pattern, ' ', author))]
    except (ValueError, SyntaxError):   
        print(f"Skipping row due to invalid tags format: {row['tags']}")
    tags_tokens = [w for w in tags_tokens if w.lower() not in stop_words and len(w) > 2]
    authors_tokens = [w for w in authors_tokens if w.lower() not in stop_words and len(w) > 2]

    # Combine tokens from all fields, recording their sources and positions
    combined_tokens = []
    sources = []
    positions = []
    current_position = 0
    
    # Add title, text, tags, and authors tokens
    current_position = process_tokens(current_position, title_tokens, combined_tokens, sources, positions, 'T')
    current_position = process_tokens(current_position, text_tokens, combined_tokens, sources, positions, 'Te')
    current_position = process_tokens(current_position, tags_tokens, combined_tokens, sources, positions, 'Ta')
    current_position = process_tokens(current_position, authors_tokens, combined_tokens, sources, positions, 'A')

    # Increment the document ID for the current row
    latest_doc_id += 1

    # Process tokens for the forward index
    for position, (token, source) in enumerate(zip(combined_tokens, sources)):
        if token not in lexicon:
            # Assign a new ID to unseen tokens and add them to the lexicon
            latest_id += 1
            lexicon[token] = latest_id
            lexicon_entries.append([latest_id, token])
        word_id = lexicon.get(token)
        
        # Determine which barrel this token belongs to
        barrel = word_id // barrel_size
        
        # Ensure the forward entries list is large enough to accommodate the barrel
        if len(forward_entries) < barrel + 1:
            forward_entries.extend([{} for _ in range(barrel - len(forward_entries) + 1)])
        
        # Initialize the document entry if it doesn't exist
        if latest_doc_id not in forward_entries[barrel]:
            forward_entries[barrel][latest_doc_id] = {}
        
        # Add token details to the forward index
        if word_id is not None:
            if word_id not in forward_entries[barrel][latest_doc_id]:
                forward_entries[barrel][latest_doc_id][word_id] = {"frequency": 0, "positions": [], "sources": []}
            forward_entries[barrel][latest_doc_id][word_id]["frequency"] += 1
            forward_entries[barrel][latest_doc_id][word_id]["positions"].append(position)
            forward_entries[barrel][latest_doc_id][word_id]["sources"].append(source)
    
    return latest_id, latest_doc_id


# Function to create inverted indexes from forward indexes
def create_inverted_index():
    barrel = 0
    while True:
        # Check if the forward index for the current barrel exists
        if os.path.isfile(forward_index_folder + f'/forward_{barrel}.csv'):
            print(f"Creating inverted barrel {barrel}...")
            update_inverted_barrel(forward_index_folder + f'/forward_{barrel}.csv', inverted_index_folder + f'/inverted_{barrel}.csv')
            create_offsets(inverted_index_folder, barrel)
            barrel += 1
        else:
            break
