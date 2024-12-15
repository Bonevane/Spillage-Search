import csv
import os
import ast
from collections import defaultdict
from forward_index import load_forward_index
import json
import re

# Load existing inverted index if it exists
def load_inverted_index(file_name):
    csv.field_size_limit(10_000_000)

    inverted_index = {}
    if os.path.exists(file_name):
        with open(file_name, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                word_id = int(row['WordID'])
                doc_ids = json.loads(row['DocIDs'])  # Convert string to list
                frequencies = json.loads(row['Frequencies'])
                positions = json.loads(row['Positions'])
                sources = re.sub('\'', '"', row['Sources'])
                sources = json.loads(sources)  # New Sources column
                inverted_index[word_id] = [doc_ids, frequencies, positions, sources]
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
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if os.stat(file_name).st_size == 0:  # Check if file is empty
            writer.writerow(['WordID', 'DocIDs', 'Frequencies', 'Positions', 'Sources'])
                
        inverted_entries = []
        for word_id in list(inverted_index.keys()):
            doc_ids = list(inverted_index[word_id].keys())
            frequencies = []
            positions = []
            sources = []
            for doc_id in doc_ids:
                frequencies.append(inverted_index[word_id][doc_id][0])
                positions.append(inverted_index[word_id][doc_id][1])
                sources.append(inverted_index[word_id][doc_id][2])
            inverted_entries.append([word_id, doc_ids, frequencies, positions, sources])
            del inverted_index[word_id]
            
        writer.writerows(inverted_entries)


def update_inverted_index(forward_index_file, inverted_index_file):
    # Load the forward index
    forward_index = load_forward_index(forward_index_file)

    # Load the existing inverted index
    inverted_index = {}
    print("LOADED")
    
    for doc_id in forward_index:
        for i in range(len(forward_index[doc_id][0])):
            word_id = forward_index[doc_id][0][i]
            if word_id not in inverted_index:
                inverted_index[word_id] = {}
            inverted_index[word_id][doc_id] = [forward_index[doc_id][1][i], forward_index[doc_id][2][i], forward_index[doc_id][3][i]]
    
    # Save only new data to the CSV file
    save_inverted_index(inverted_index, inverted_index_file)
    print("Inverted index has been updated and saved.")