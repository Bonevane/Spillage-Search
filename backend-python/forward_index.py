import re
import csv
import os
import json


# Load existing forward index from a file
def load_forward_barrel(file_name):
    forward_barrel = {}
    if os.path.exists(file_name):
        with open(file_name, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                doc_id = int(row['DocID'])
                word_ids = json.loads(row['WordIDs'])  # Convert string to list
                frequencies = json.loads(row['Frequencies'])
                positions = json.loads(row['Positions'])
                sources = re.sub('\'', '"', row['Sources'])
                sources = json.loads(sources)  # New Sources column
                forward_barrel[doc_id] = [word_ids, frequencies, positions, sources]
    return forward_barrel


# Save forward index to a file
def save_forward_index(forward_index, folder_name):
    os.makedirs(folder_name, exist_ok=True)
    for barrel in range(len(forward_index)):
        file_name = folder_name + f"/forward_{barrel}.csv"
        with open(file_name, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write the header
            if os.stat(file_name).st_size == 0:
                writer.writerow(['DocID', 'WordIDs', 'Frequencies', 'Positions', 'Sources'])
            
            forward_entries = []
            for doc_id, word_data in forward_index[barrel].items():
                # Extract WordIDs, Frequencies, Positions, and Sources
                word_ids = list(word_data.keys())
                frequencies = [data['frequency'] for data in word_data.values()]
                positions = [data['positions'] for data in word_data.values()]
                sources = [data['sources'] for data in word_data.values()]
                forward_entries.append([doc_id, word_ids, frequencies, positions, sources])
                
            writer.writerows(forward_entries)