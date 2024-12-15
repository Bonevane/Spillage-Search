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

barrel_size = 1001

def iterate_dataset(dataset_file, lexicon_file):
    stop_words = set(stopwords.words('english'))
    processed_set = load_processed_entries()
    lexicon = load_lexicon(lexicon_file)
    latest_doc_id = load_latest_doc_id()
    latest_id = load_latest_id()
    
    with open(dataset_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        forward_entries = []
        lexicon_entries = []
        
        for row in csv_reader:
            current_entry = (row['title'], row['url'], row['authors'], row['timestamp'], row['tags'])
            if current_entry in processed_set: # Skip processing if document already exists
                continue
            
            latest_id, latest_doc_id = index_dataset(row, stop_words, latest_doc_id, latest_id, lexicon, lexicon_entries, forward_entries)

            processed_set.add(current_entry)
            save_processed_docs([[latest_doc_id, row['title'], row['url'], row['authors'], row['timestamp'], row['tags']]], latest_doc_id)
            
            if latest_doc_id % barrel_size == 0:
                save_words_to_lexicon(lexicon, lexicon_entries, latest_id)
                save_forward_index(forward_entries, forward_index_folder)
                lexicon_entries.clear()
                forward_entries.clear()
                print(f"Writing batch {latest_doc_id - barrel_size} to {latest_doc_id}...")
        
        if forward_entries:
            save_words_to_lexicon(lexicon, lexicon_entries, latest_id)
            save_forward_index(forward_entries, forward_index_folder)
            print(f"Writing batch {latest_doc_id - (latest_doc_id % barrel_size)} to {latest_doc_id}...")


def index_dataset(row, stop_words, latest_doc_id, latest_id, lexicon, lexicon_entries, forward_entries):
    pattern = r'[^A-Za-z0-9 ]+'
    combined_tokens = []
    new_entries = []
    new_doc_entries = []
    
    # Process individual fields with lemmatization
    title_tokens = [preprocess_word(token) for token in word_tokenize(re.sub(r'[^A-Za-z ]+', ' ', row['title']))]
    title_tokens = [w for w in title_tokens if w.lower() not in stop_words and len(w) > 2]

    text_tokens = []
    for paragraph in row['text'].split("\n"):
        for token in word_tokenize(re.sub(r'[^A-Za-z ]+', ' ', paragraph)):
            text_tokens.append(preprocess_word(token))
    text_tokens = [w for w in text_tokens if w.lower() not in stop_words and len(w) > 2]
    
    # A lil error error handling because the dataset is not clean yet (after around 1200ish entries it goes haywire in the articles dataset)
    try:
        tags_tokens = [preprocess_word(token) for tag in ast.literal_eval(row['tags']) for token in word_tokenize(re.sub(r'[^A-Za-z ]+', ' ', tag))]
        authors_tokens = [preprocess_word(token) for author in ast.literal_eval(row['authors']) for token in word_tokenize(re.sub(r'[^A-Za-z ]+', ' ', author))]
    except (ValueError, SyntaxError):   
        print(f"Skipping row due to invalid tags format: {row['tags']}")
    tags_tokens = [w for w in tags_tokens if w.lower() not in stop_words and len(w) > 2]
    authors_tokens = [w for w in authors_tokens if w.lower() not in stop_words and len(w) > 2]

    # Create a single combined list of tokens with positions and sources
    combined_tokens = []
    sources = []
    positions = []

    # Add tokens and sources from title
    combined_tokens.extend(title_tokens)
    sources.extend(['T'] * len(title_tokens))
    positions.extend(list(range(len(title_tokens))))

    # Add tokens and sources from text (each paragraph separately)
    current_position = len(title_tokens)
    combined_tokens.extend(text_tokens)
    sources.extend(['Te'] * len(text_tokens))
    positions.extend(list(range(current_position, current_position + len(text_tokens))))
    current_position += len(text_tokens)

    # Add tokens and sources from tags
    combined_tokens.extend(tags_tokens)
    sources.extend(['Ta'] * len(tags_tokens))
    positions.extend(list(range(current_position, current_position + len(tags_tokens))))
    current_position += len(tags_tokens)

    # Add tokens and sources from authors
    combined_tokens.extend(authors_tokens)
    sources.extend(['A'] * len(authors_tokens))
    positions.extend(list(range(current_position, current_position + len(authors_tokens))))
    current_position += len(authors_tokens)

    latest_doc_id += 1
    # Process each token for the current document
    for position, (token, source) in enumerate(zip(combined_tokens, sources)):
        if token not in lexicon:
            latest_id += 1
            lexicon[token] = latest_id
            lexicon_entries.append([latest_id, token])
        word_id = lexicon.get(token)  # Get the word ID from the lexicon
        
        barrel = word_id // barrel_size
        
        if len(forward_entries) < barrel + 1:
            forward_entries.extend([{} for i in range(barrel - len(forward_entries) + 1)])
        try:
            forward_entries[barrel][latest_doc_id]
        except KeyError:
            forward_entries[barrel][latest_doc_id] = {}
        if word_id is not None:  # Skip tokens not in the lexicon
            if word_id not in forward_entries[barrel][latest_doc_id]:
                forward_entries[barrel][latest_doc_id][word_id] = {"frequency": 0, "positions": [], "sources": []}
            forward_entries[barrel][latest_doc_id][word_id]["frequency"] += 1
            forward_entries[barrel][latest_doc_id][word_id]["positions"].append(position)
            forward_entries[barrel][latest_doc_id][word_id]["sources"].append(source)

    combined_tokens = list(dict.fromkeys(combined_tokens))
    
    return latest_id, latest_doc_id


def create_inverted_index():
    barrel = 0
    while True:
        if os.path.isfile(forward_index_folder + f'/forward_{barrel}.csv'):
            print(f"Creating inverted barrel {barrel}...")
            update_inverted_barrel(forward_index_folder + f'/forward_{barrel}.csv', inverted_index_folder + f'/inverted_{barrel}.csv')
            create_offsets(inverted_index_folder, barrel)
            barrel += 1
        else:
            break