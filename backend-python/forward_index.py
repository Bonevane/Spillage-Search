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
    if os.path.exists(file_name):
        with open(file_name, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                doc_id = int(row['DocID'])
                word_ids = ast.literal_eval(row['WordIDs'])  # Convert string to list
                frequencies = ast.literal_eval(row['Frequencies'])
                positions = ast.literal_eval(row['Positions'])
                sources = ast.literal_eval(row['Sources'])  # New Sources column
                for word_id, frequency, position_list, source_list in zip(word_ids, frequencies, positions, sources):
                    forward_index[doc_id][word_id]["frequency"] = frequency
                    forward_index[doc_id][word_id]["positions"] = position_list
                    forward_index[doc_id][word_id]["sources"] = source_list
    return forward_index

# Save forward index to a file
def save_forward_index(forward_index, file_name):
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['DocID', 'WordIDs', 'Frequencies', 'Positions', 'Sources'])
        for doc_id, word_data in forward_index.items():
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
    forward_index = load_forward_index(output_file)
    
    # Get existing DocIDs to avoid reprocessing
    existing_doc_ids = set(forward_index.keys())

    # Read dataset and process documents
    with open(dataset_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for doc_id, row in enumerate(csv_reader, start=1):
            if doc_id in existing_doc_ids:        # Skip processing if docID already exists
                continue

            # Process individual fields with lemmatization
            title_tokens = [preprocess_word(token) for token in word_tokenize(re.sub(r'[^A-Za-z ]+', '', row['title']))]
            text_tokens = [
                [preprocess_word(token) for token in word_tokenize(re.sub(r'[^A-Za-z ]+', '', paragraph))]
                for paragraph in row['text'].split("\n")
            ]
            
            # A lil error error handling because the dataset is not clean yet (after around 1200ish entries it goes haywire in the articles dataset)
            try:
                tags_tokens = [preprocess_word(token) for tag in ast.literal_eval(row['tags']) for token in word_tokenize(re.sub(r'[^A-Za-z ]+', '', tag))]
                authors_tokens = [preprocess_word(token) for author in ast.literal_eval(row['authors']) for token in word_tokenize(re.sub(r'[^A-Za-z ]+', '', author))]
            except (ValueError, SyntaxError):
                print(f"Skipping row due to invalid tags format: {row['tags']}")
                tags_tokens = []
                authors_tokens = []
            
            # Set boundaries for each section
            title_end = len(title_tokens)
            text_end = title_end + sum(len(paragraph) for paragraph in text_tokens)
            tag_end = text_end + len(tags_tokens)
            author_end = tag_end + len(authors_tokens)

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
            for paragraph in text_tokens:
                combined_tokens.extend(paragraph)
                sources.extend(['Te'] * len(paragraph))
                positions.extend(list(range(current_position, current_position + len(paragraph))))
                current_position += len(paragraph)

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

            # Process each token for the current document
            forward_index[doc_id] = defaultdict(lambda: {"frequency": 0, "positions": [], "sources": []})
            for position, (token, source) in enumerate(zip(combined_tokens, sources)):
                word_id = lexicon.get(token)  # Get the word ID from the lexicon
                if word_id is not None:  # Skip tokens not in the lexicon
                    if word_id not in forward_index[doc_id]:
                        forward_index[doc_id][word_id] = {"frequency": 0, "positions": [], "sources": []}
                    forward_index[doc_id][word_id]["frequency"] += 1
                    forward_index[doc_id][word_id]["positions"].append(position)
                    forward_index[doc_id][word_id]["sources"].append(source)

    # Save the updated forward index
    save_forward_index(forward_index, output_file)
    print("Forward index with sources has been updated or created.")
