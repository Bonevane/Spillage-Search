import csv
import os
import ast
from collections import defaultdict
from forward_index import load_forward_index

# Load existing inverted index if it exists
def load_inverted_index(file_name):
    inverted_index = defaultdict(lambda: {"doc_ids": [], "frequencies": [], "positions": [], "sources": []})
    if os.path.exists(file_name):
        with open(file_name, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                word_id = int(row['WordID'])
                doc_ids = ast.literal_eval(row['DocIDs'])
                frequencies = ast.literal_eval(row['Frequencies'])
                positions = ast.literal_eval(row['Positions'])
                sources = ast.literal_eval(row['Sources'])
                inverted_index[word_id]["doc_ids"] = doc_ids
                inverted_index[word_id]["frequencies"] = frequencies
                inverted_index[word_id]["positions"] = positions
                inverted_index[word_id]["sources"] = sources
    return inverted_index

def save_inverted_index(inverted_index, file_name):
    # Load existing WordIDs to avoid duplicate entries
    existing_word_ids = set()
    if os.path.exists(file_name):
        with open(file_name, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                existing_word_ids.add(int(row['WordID']))
    
    # Open the file in append mode
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if os.stat(file_name).st_size == 0:  # Check if file is empty
            writer.writerow(['WordID', 'DocIDs', 'Frequencies', 'Positions', 'Sources'])

        # Append new WordIDs
        for word_id, data in inverted_index.items():
            if word_id not in existing_word_ids:  # Skip if WordID already exists
                writer.writerow([
                    word_id,
                    data["doc_ids"],
                    data["frequencies"],
                    data["positions"],
                    data["sources"]
                ])

def update_inverted_index(forward_index_file, inverted_index_file):
    # Load the forward index
    forward_index = load_forward_index(forward_index_file)

    # Load the existing inverted index
    inverted_index = load_inverted_index(inverted_index_file)

    # Iterate over each document in the forward index
    for doc_id, word_data in forward_index.items():
        # For each word in the document, update the inverted index
        for word_id, data in word_data.items():
            if doc_id not in inverted_index[word_id]["doc_ids"]:
                inverted_index[word_id]["doc_ids"].append(doc_id)
                inverted_index[word_id]["frequencies"].append(data["frequency"])
                inverted_index[word_id]["positions"].append(data["positions"])
                inverted_index[word_id]["sources"].append(data["sources"])
    
    # Save only new data to the CSV file
    save_inverted_index(inverted_index, inverted_index_file)
    print("Inverted index has been updated and saved.")
