import os
import csv
from nltk.stem import WordNetLemmatizer
from config import lexicon_file, id_file

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

def preprocess_word(word):
    word = word.lower()
    lemmatized_word = lemmatizer.lemmatize(word, pos="v")
    if lemmatized_word != word:
        return lemmatized_word

    # Try lemmatizing as noun
    lemmatized_word = lemmatizer.lemmatize(word, pos="n")
    if lemmatized_word != word:
        return lemmatized_word

    # Try lemmatizing as adjective
    lemmatized_word = lemmatizer.lemmatize(word, pos="a")
    if lemmatized_word != word:
        return lemmatized_word

    # Try lemmatizing as adverb
    lemmatized_word = lemmatizer.lemmatize(word, pos="r")
    return lemmatized_word

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


def save_words_to_lexicon(lexicon_dict, new_entries, latest_id):
    # Append new entries to the CSV
    with open(lexicon_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if os.stat(lexicon_file).st_size == 0:
            writer.writerow(['ID', 'Word'])
        writer.writerows(new_entries)

    # Save the latest ID
    with open(id_file, 'w') as file:
        file.write(str(latest_id))