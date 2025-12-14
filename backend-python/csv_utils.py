import csv
import os
import json
import re
from typing import Dict, List, Any, Set, Tuple
from config import id_file, doc_id_file, processed_file
import numpy as np

#
#   ALL TO DO WITH REMEMBERING THE LATEST IDS AND WHAT FILES HAVE BEEN PROCESSED
#  

def load_latest_id() -> int:
    # Read the latest ID from the file
    if os.path.exists(id_file):
        with open(id_file, 'r') as file:
            content = file.read().strip()
            latest_id = int(content) if content else 0
    else:
        latest_id = 0
    return latest_id


def load_latest_doc_id() -> int:

    if os.path.exists(doc_id_file):
        with open(doc_id_file, 'r') as file:
            content = file.read().strip()
            latest_doc_id = int(content) if content else 0
    else:
        latest_doc_id = 0
    return latest_doc_id


def save_processed_docs(new_entries: List[List[Any]], latest_doc_id: int) -> None:
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


def load_processed_entries() -> Set[Tuple[Any, ...]]:
    processed_set = set()

    if os.path.exists(processed_file):
        with open(processed_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                processed_set.add(tuple(row[1:]))
    return processed_set


def load_processed_to_dict(file_path: str) -> Dict[int, Dict[str, Any]]:
    data_dict: Dict[int, Dict[str, Any]] = {}
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} does not exist.")
        return data_dict

    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)  # Read rows as dictionaries
        for row in csv_reader:
            if not row.get('ID'):
                continue
            row_id = int(row['ID'])  # Use the 'ID' column as the key
            tags_str = re.sub('\'', '"', row.get('tags', '[]'))
            authors_str = re.sub('\'', '"', row.get('authors', '[]'))
            try:
                data_dict[row_id] = {
                    'title': row.get('title', ''),
                    'url': row.get('url', ''),
                    'authors': json.loads(authors_str),
                    'timestamp': row.get('timestamp', ''),
                    'tags': json.loads(tags_str)
                }
            except:
                data_dict[row_id] = {
                    'title': row.get('title', ''),
                    'url': row.get('url', ''),
                    'authors': [],
                    'timestamp': row.get('timestamp', ''),
                    'tags': json.loads(tags_str)
                }
    print("Processed data loaded!")
    return data_dict

def load_scrapped_to_dict(file_path: str) -> Dict[int, Dict[str, Any]]:
    data_dict: Dict[int, Dict[str, Any]] = {}
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} does not exist.")
        return data_dict

    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)  # Read rows as dictionaries 
        for row in csv_reader:
            if not row.get('ID'):
                continue
            row_id = int(row['ID'])  # Use the 'ID' column as the key
            data_dict[row_id] = {
                'url': row.get('URL', ''),
                'description': row.get('Description', ''),
                'member only': row.get('Member Only', ''),
                'code': row.get('Code', '')
            }
    print("Scrapped data loaded!")
    return data_dict

def calculate_lengths() -> None:
    with open('datasets/medium_articles.csv', 'r', encoding='utf-8') as infile, \
        open('indexes/lengths.csv', 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=['ID', 'length'])
        writer.writeheader()
        for idx, row in enumerate(reader, start=1):
            text = row.get('text', '')
            word_count = len(text.split()) if text else 0
            writer.writerow({'ID': idx, 'length': word_count})
            print(f"Processed {idx} rows.")

def load_lengths(file_path: str) -> Dict[int, int]:
    data_dict: Dict[int, int] = {}
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} does not exist.")
        return data_dict

    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)  # Read rows as dictionaries
        for row in csv_reader:
            if not row.get('ID'):
                continue
            row_id = int(row['ID'])  # Use the 'ID' column as the key
            data_dict[row_id] = int(row['length'])
    print("Lengths data loaded!")
    return data_dict

