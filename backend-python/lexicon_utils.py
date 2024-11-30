import os
import csv
from nltk.stem import WordNetLemmatizer

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

def preprocess_word(word):
    return lemmatizer.lemmatize(word.lower())

def save_words_to_lexicon(filtered_words):
    lexicon_file = 'lexicon.csv'
    id_file = 'latest_id.txt'
    lexicon_dict = {}

    # Read the latest ID from the file
    if os.path.exists(id_file):
        with open(id_file, 'r') as file:
            latest_id = int(file.read().strip())
    else:
        latest_id = 0

    # Load existing lexicon
    if os.path.exists(lexicon_file):
        with open(lexicon_file, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header
            for row in csv_reader:
                lexicon_dict[row[1]] = int(row[0])

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
