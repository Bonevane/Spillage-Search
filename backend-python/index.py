import os
import csv
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from csv_utils import load_latest_id, load_latest_doc_id, save_processed_docs, load_processed_entries
from lexicon_utils import load_lexicon, preprocess_word, save_words_to_lexicon
from collections import defaultdict
import re
import nltk
import ast

# Save forward index to a file
def save_forward_index(forward_index, file_name):
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        if os.stat(file_name).st_size == 0:
            writer.writerow(['DocID', 'WordIDs', 'Frequencies', 'Positions', 'Sources'])
        
        forward_entries = []
        for doc_id, word_data in forward_index.items():
            # Extract WordIDs, Frequencies, Positions, and Sources
            word_ids = list(word_data.keys())
            frequencies = [data['frequency'] for data in word_data.values()]
            positions = [data['positions'] for data in word_data.values()]
            sources = [data['sources'] for data in word_data.values()]
            forward_entries.append([doc_id, word_ids, frequencies, positions, sources])
            
        writer.writerows(forward_entries)


def iterate_dataset(dataset_file, lexicon_file):
    stop_words = set(stopwords.words('english'))
    processed_set = load_processed_entries()
    lexicon = load_lexicon(lexicon_file)
    output_file = 'indices/forward_index.csv'
    latest_doc_id = load_latest_doc_id()
    latest_id = load_latest_id()
    batch_size = 1000
    
    with open(dataset_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        forward_entries = defaultdict(lambda: defaultdict(lambda: {"frequency": 0, "positions": [], "sources": []}))
        lexicon_entries = []
        
        for row in csv_reader:
            current_entry = (row['title'], row['url'], row['authors'], row['timestamp'], row['tags'])
            if current_entry in processed_set: # Skip processing if document already exists
                continue
            
            latest_id, latest_doc_id = index_dataset(row, stop_words, latest_doc_id, latest_id, lexicon, lexicon_entries, forward_entries)

            processed_set.add(current_entry)
            save_processed_docs([[latest_doc_id, row['title'], row['url'], row['authors'], row['timestamp'], row['tags']]], latest_doc_id)
            
            if latest_doc_id % batch_size == 0:
                save_words_to_lexicon(lexicon, lexicon_entries, latest_id)
                save_forward_index(forward_entries, output_file)
                lexicon_entries.clear()
                forward_entries.clear()
                print(f"Writing batch {latest_doc_id - batch_size} to {latest_doc_id}...")
        
        if forward_entries:
            save_words_to_lexicon(lexicon, lexicon_entries, latest_id)
            save_forward_index(forward_entries, output_file)
            print(f"Writing batch {latest_doc_id - (latest_doc_id % batch_size)} to {latest_doc_id}...")


def index_dataset(row, stop_words, latest_doc_id, latest_id, lexicon, lexicon_entries, forward_entries):
    pattern = r'[^A-Za-z0-9 ]+'
    combined_tokens = []
    new_entries = []
    new_doc_entries = []
    
    batch_count = 0
    
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
    tags_tokens = []
    authors_tokens = []
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
    forward_entries[latest_doc_id] = defaultdict(lambda: {"frequency": 0, "positions": [], "sources": []})
    for position, (token, source) in enumerate(zip(combined_tokens, sources)):
        if token not in lexicon:
            latest_id += 1
            lexicon[token] = latest_id
            lexicon_entries.append([latest_id, token])
        word_id = lexicon.get(token)  # Get the word ID from the lexicon
        if word_id is not None:  # Skip tokens not in the lexicon
            if word_id not in forward_entries[latest_doc_id]:
                forward_entries[latest_doc_id][word_id] = {"frequency": 0, "positions": [], "sources": []}
            forward_entries[latest_doc_id][word_id]["frequency"] += 1
            forward_entries[latest_doc_id][word_id]["positions"].append(position)
            forward_entries[latest_doc_id][word_id]["sources"].append(source)

    combined_tokens = list(dict.fromkeys(combined_tokens))
    
    batch_count += 1
    #print(f"Batch {batch_count} saved.")
    
    return latest_id, latest_doc_id