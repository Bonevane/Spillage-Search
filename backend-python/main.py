from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import nltk
import csv
from lexicon_utils import preprocess_word, save_words_to_lexicon
from csv_utils import load_latest_doc_id, save_processed_docs, load_processed_entries

# NLTK downloads
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

def extract_filtered_words_from_csv(csv_filename):
    stop_words = set(stopwords.words('english'))
    pattern = r'[^A-Za-z ]+'
    chunk_size = 10000
    filtered_words = []
    new_entries = []
    latest_doc_id = load_latest_doc_id()
    processed_set = load_processed_entries()

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
                    save_words_to_lexicon(filtered_words)
                    filtered_words.clear()

            if filtered_words:
                filtered_words = list(dict.fromkeys(filtered_words))
                save_words_to_lexicon(filtered_words)
            save_processed_docs(new_entries, latest_doc_id)

    except FileNotFoundError:
        print(f"File not found: {csv_filename}")
    except KeyError as e:
        print(f"Missing column in CSV: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the program
csv_file = "test.csv"
extract_filtered_words_from_csv(csv_file)
