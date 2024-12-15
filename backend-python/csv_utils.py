import csv
import os

def load_latest_id():
    id_file = 'indices/latest_id.txt'

    # Read the latest ID from the file
    if os.path.exists(id_file):
        with open(id_file, 'r') as file:
            latest_id = int(file.read().strip())
    else:
        latest_id = 0
    return latest_id

def load_latest_doc_id():
    doc_id_file = 'indices/latest_doc_id.txt'
    if os.path.exists(doc_id_file):
        with open(doc_id_file, 'r') as file:
            latest_doc_id = int(file.read().strip())
    else:
        latest_doc_id = 0
    return latest_doc_id

def save_processed_docs(new_entries, latest_doc_id):
    processed_file = 'indices/processed.csv'
    doc_id_file = 'indices/latest_doc_id.txt'

    # Append new entries to the CSV
    with open(processed_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if os.stat(processed_file).st_size == 0:
            writer.writerow(['ID', 'title', 'url', 'authors', 'timestamp', 'tags'])
        writer.writerows(new_entries)

    # Save the latest ID
    with open(doc_id_file, 'w') as file:
        file.write(str(latest_doc_id))

def load_processed_entries():
    processed_file = 'indices/processed.csv'
    processed_set = set()

    if os.path.exists(processed_file):
        with open(processed_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip the header
            for row in reader:
                processed_set.add(tuple(row[1:]))
    return processed_set
