from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
from lexicon_utils import load_lexicon, preprocess_word
import re
import csv
import os
import nltk
import ast

nltk.download('punkt')      # For word tokenization
nltk.download('stopwords')  # If using stop words
nltk.download('wordnet')  

# Initialize lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Load existing forward index from a file
def load_forward_index(file_name):
    forward_index = defaultdict(lambda: defaultdict(lambda: {"frequency": 0, "positions": [], "sources": []}))
    existing_doc_ids = set()  # Keep track of existing DocIDs
    if os.path.exists(file_name):
        with open(file_name, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                doc_id = int(row['DocID'])
                existing_doc_ids.add(doc_id)
                word_ids = ast.literal_eval(row['WordIDs'])  # Convert string to list
                frequencies = ast.literal_eval(row['Frequencies'])
                positions = ast.literal_eval(row['Positions'])
                sources = ast.literal_eval(row['Sources'])  # New Sources column
                for word_id, frequency, position_list, source_list in zip(word_ids, frequencies, positions, sources):
                    forward_index[doc_id][word_id]["frequency"] = frequency
                    forward_index[doc_id][word_id]["positions"] = position_list
                    forward_index[doc_id][word_id]["sources"] = source_list
    return forward_index, existing_doc_ids

# Save forward index to a file
def save_forward_index(forward_index, file_name, existing_doc_ids):
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write the header if the file is empty
        if os.stat(file_name).st_size == 0:
            writer.writerow(['DocID', 'WordIDs', 'Frequencies', 'Positions', 'Sources'])
        
        for doc_id, word_data in forward_index.items():
            if doc_id in existing_doc_ids:  # Skip if DocID already exists
                continue
            # Extract WordIDs, Frequencies, Positions, and Sources
            word_ids = list(word_data.keys())
            frequencies = [data['frequency'] for data in word_data.values()]
            positions = [data['positions'] for data in word_data.values()]
            sources = [data['sources'] for data in word_data.values()]
            # Write the row
            writer.writerow([doc_id, word_ids, frequencies, positions, sources])

def update_forward_index(dataset_file, lexicon_file, output_file):
    # Load lexicon
    lexicon = load_lexicon(lexicon_file)
    
    # Load existing forward index if it exists
    forward_index, existing_doc_ids = load_forward_index(output_file)
    
    batch_forward_index = defaultdict(lambda: defaultdict(lambda: {"frequency": 0, "positions": [], "sources": []}))
    chunk_size = 1000
    batch_count = 0

    # Read dataset and process documents
    with open(dataset_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for doc_id, row in enumerate(csv_reader, start=1):
            if doc_id in existing_doc_ids:  # Skip processing if docID already exists
                continue

            # Process individual fields with lemmatization
            title_tokens = [preprocess_word(token) for token in word_tokenize(re.sub(r'[^A-Za-z ]+', '', row['title']))]
            text_tokens = [
                [preprocess_word(token) for token in word_tokenize(re.sub(r'[^A-Za-z ]+', '', paragraph))]
                for paragraph in row['text'].split("\n")
            ]
            
            try:
                tags_tokens = [preprocess_word(token) for tag in ast.literal_eval(row['tags']) for token in word_tokenize(re.sub(r'[^A-Za-z ]+', '', tag))]
                authors_tokens = [preprocess_word(token) for author in ast.literal_eval(row['authors']) for token in word_tokenize(re.sub(r'[^A-Za-z ]+', '', author))]
            except (ValueError, SyntaxError):
                print(f"Skipping row due to invalid tags format: {row['tags']}")
                tags_tokens = []
                authors_tokens = []
            
            title_end = len(title_tokens)
            text_end = title_end + sum(len(paragraph) for paragraph in text_tokens)
            tag_end = text_end + len(tags_tokens)
            author_end = tag_end + len(authors_tokens)

            combined_tokens = []
            sources = []
            positions = []

            combined_tokens.extend(title_tokens)
            sources.extend(['T'] * len(title_tokens))
            positions.extend(list(range(len(title_tokens))))

            current_position = len(title_tokens)
            for paragraph in text_tokens:
                combined_tokens.extend(paragraph)
                sources.extend(['Te'] * len(paragraph))
                positions.extend(list(range(current_position, current_position + len(paragraph))))
                current_position += len(paragraph)

            combined_tokens.extend(tags_tokens)
            sources.extend(['Ta'] * len(tags_tokens))
            positions.extend(list(range(current_position, current_position + len(tags_tokens))))
            current_position += len(tags_tokens)

            combined_tokens.extend(authors_tokens)
            sources.extend(['A'] * len(authors_tokens))
            positions.extend(list(range(current_position, current_position + len(authors_tokens))))
            current_position += len(authors_tokens)

            batch_forward_index[doc_id] = defaultdict(lambda: {"frequency": 0, "positions": [], "sources": []})
            for position, (token, source) in enumerate(zip(combined_tokens, sources)):
                word_id = lexicon.get(token)
                if word_id is not None:
                    if word_id not in batch_forward_index[doc_id]:
                        batch_forward_index[doc_id][word_id] = {"frequency": 0, "positions": [], "sources": []}
                    batch_forward_index[doc_id][word_id]["frequency"] += 1
                    batch_forward_index[doc_id][word_id]["positions"].append(position)
                    batch_forward_index[doc_id][word_id]["sources"].append(source)
            
            if doc_id % chunk_size == 0:
                save_forward_index(batch_forward_index, output_file, existing_doc_ids)
                batch_forward_index.clear()
                batch_count += 1
                print(f"Batch {batch_count} saved.")

    if batch_forward_index:
        save_forward_index(batch_forward_index, output_file, existing_doc_ids)
        print("Forward index with sources has been updated or created.")
