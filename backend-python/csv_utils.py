import csv
import os
import json
import re
from config import id_file, doc_id_file, processed_file
from sentence_transformers import SentenceTransformer, util
import numpy as np

#
#   ALL TO DO WITH REMEMBERING THE LATEST IDS AND WHAT FILES HAVE BEEN PROCESSED
#  

def load_latest_id():
    # Read the latest ID from the file
    if os.path.exists(id_file):
        with open(id_file, 'r') as file:
            latest_id = int(file.read().strip())
    else:
        latest_id = 0
    return latest_id


def load_latest_doc_id():

    if os.path.exists(doc_id_file):
        with open(doc_id_file, 'r') as file:
            latest_doc_id = int(file.read().strip())
    else:
        latest_doc_id = 0
    return latest_doc_id


def save_processed_docs(new_entries, latest_doc_id):
    os.makedirs("indexes", exist_ok=True)

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
    processed_set = set()

    if os.path.exists(processed_file):
        with open(processed_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                processed_set.add(tuple(row[1:]))
    return processed_set


def load_processed_to_dict(file_path):
    data_dict = {}
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)  # Read rows as dictionaries
        for row in csv_reader:
            row_id = int(row['ID'])  # Use the 'ID' column as the key
            tags = re.sub('\'', '"', row['tags'])
            try:
                data_dict[row_id] = {
                    'title': row['title'],
                    'url': row['url'],
                    'authors': row['authors'],
                    'timestamp': row['timestamp'],
                    'tags': json.loads(tags)
                }
            except:
                print("Error in tags")
    print("Processed data loaded!")
    return data_dict

def load_scrapped_to_dict(file_path):
    data_dict = {}
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)  # Read rows as dictionaries 
        for row in csv_reader:
            row_id = int(row['ID'])  # Use the 'ID' column as the key
            data_dict[row_id] = {
                'url': row['URL'],
                'description': row['Description'],
                'member only': row['Member Only'],
                'code': row['Code']
            }
    print("Scrapped data loaded!")
    return data_dict

def calculate_lengths():
    with open('datasets/medium_articles.csv', 'r', encoding='utf-8') as infile, \
        open('indexes/lengths.csv', 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=['ID', 'length'])
        writer.writeheader()
        for idx, row in enumerate(reader, start=1):
            text = row.get('text', '')
            word_count = len(text.split())
            writer.writerow({'ID': idx, 'length': word_count})
            print(f"Processed {idx} rows.")

def load_lengths(file_path):
    data_dict = {}
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)  # Read rows as dictionaries
        for row in csv_reader:
            row_id = int(row['ID'])  # Use the 'ID' column as the key
            data_dict[row_id] = int(row['length'])
    print("Lengths data loaded!")
    return data_dict

