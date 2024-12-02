import os
import csv
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from csv_utils import load_latest_doc_id, save_processed_docs, load_processed_entries
import re
import nltk

# NLTK downloads
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

def preprocess_word(word):
    return lemmatizer.lemmatize(word.lower())

# Load lexicon
def load_lexicon(lexicon_file):
    lexicon = {}
    if os.path.exists(lexicon_file):
        with open(lexicon_file, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header
            for row in csv_reader:
                lexicon[row[1]] = int(row[0])  # Map word to wordID
    print("Lexicon Loaded!")
    return lexicon

def save_words_to_lexicon(filtered_words, lexicon_dict):
    lexicon_file = 'lexicon.csv'
    id_file = 'latest_id.txt'

    # Read the latest ID from the file
    if os.path.exists(id_file):
        with open(id_file, 'r') as file:
            latest_id = int(file.read().strip())
    else:
        latest_id = 0

    # Add new words to the lexicon
    new_entries = []
    for word in filtered_words:
        if word not in lexicon_dict:
            latest_id += 1
            lexicon_dict[word] = latest_id
            new_entries.append([latest_id, word])

    # Append new entries to the CSV
    with open(lexicon_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if os.stat(lexicon_file).st_size == 0:
            writer.writerow(['ID', 'Word'])
        writer.writerows(new_entries)

    # Save the latest ID
    with open(id_file, 'w') as file:
        file.write(str(latest_id))

    print("Words have been saved to the lexicon.")


def create_and_update_lexicon(csv_filename, lexicon_file):
    stop_words = set(stopwords.words('english'))
    pattern = r'[^A-Za-z ]+'
    chunk_size = 1000
    filtered_words = []
    new_entries = []
    latest_doc_id = load_latest_doc_id()
    processed_set = load_processed_entries()
    lexicon = load_lexicon(lexicon_file)

    try:
        with open(csv_filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            row_count = 0

            for row in reader:
                current_entry = (row['title'], row['url'], row['authors'], row['timestamp'], row['tags'])
                if current_entry in processed_set:
                    continue

                combined_text = f"{row['title']} {row['text']} {row['authors']} {row['tags']}"
                clean_text = re.sub(pattern, ' ', combined_text)
                tokens = word_tokenize(clean_text)
                filtered_words.extend(
                    preprocess_word(w) for w in tokens
                    if w.lower() not in stop_words and len(w) > 2
                )

                row_count += 1
                latest_doc_id += 1
                new_entries.append([latest_doc_id, row['title'], row['url'], row['authors'], row['timestamp'], row['tags']])
                processed_set.add(current_entry)

                if row_count % chunk_size == 0:
                    filtered_words = list(dict.fromkeys(filtered_words))
                    save_words_to_lexicon(filtered_words, lexicon)
                    filtered_words.clear()

            if filtered_words:
                filtered_words = list(dict.fromkeys(filtered_words))
                save_words_to_lexicon(filtered_words, lexicon)
            save_processed_docs(new_entries, latest_doc_id)

    except FileNotFoundError:
        print(f"File not found: {csv_filename}")
    except KeyError as e:
        print(f"Missing column in CSV: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")