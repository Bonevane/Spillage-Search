import csv
import json
import struct
import os
import re
import shutil
from nltk.tokenize import word_tokenize
from collections import defaultdict

def preprocess_word(word):
    """Clean and preprocess a word"""
    return re.sub(r'[^A-Za-z0-9]', '', word).lower()

def process_scraped_article_tokens(article_data, stop_words):
    """
    Process scraped article data and extract tokens with positions and sources
    Similar to the index_dataset function but for scraped articles
    """
    print(f"DEBUG: Starting token processing for article: {article_data['title'][:50]}...")
    
    pattern = r'[^A-Za-z0-9 ]+'
    
    # Process title tokens
    print("DEBUG: Processing title tokens...")
    title_tokens = [preprocess_word(token) for token in word_tokenize(re.sub(pattern, ' ', article_data['title']))]
    title_tokens = [w for w in title_tokens if w.lower() not in stop_words and len(w) > 2]
    print(f"DEBUG: Found {len(title_tokens)} valid title tokens")
    
    # Process text tokens
    print("DEBUG: Processing text tokens...")
    text_tokens = []
    for paragraph in article_data['text'].split("\\n"):
        for token in word_tokenize(re.sub(pattern, ' ', paragraph)):
            text_tokens.append(preprocess_word(token))
    text_tokens = [w for w in text_tokens if w.lower() not in stop_words and len(w) > 2]
    print(f"DEBUG: Found {len(text_tokens)} valid text tokens")
    
    # Process tags tokens
    print("DEBUG: Processing tags tokens...")
    tags_tokens = []
    try:
        if isinstance(article_data['tags'], list):
            for tag in article_data['tags']:
                for token in word_tokenize(re.sub(pattern, ' ', str(tag))):
                    tags_tokens.append(preprocess_word(token))
        tags_tokens = [w for w in tags_tokens if w.lower() not in stop_words and len(w) > 2]
        print(f"DEBUG: Found {len(tags_tokens)} valid tag tokens")
    except Exception as e:
        print(f"DEBUG: Error processing tags: {e}")
        tags_tokens = []
    
    # Process authors tokens
    print("DEBUG: Processing author tokens...")
    authors_tokens = []
    try:
        if isinstance(article_data['authors'], list):
            for author in article_data['authors']:
                for token in word_tokenize(re.sub(pattern, ' ', str(author))):
                    authors_tokens.append(preprocess_word(token))
        authors_tokens = [w for w in authors_tokens if w.lower() not in stop_words and len(w) > 2]
        print(f"DEBUG: Found {len(authors_tokens)} valid author tokens")
    except Exception as e:
        print(f"DEBUG: Error processing authors: {e}")
        authors_tokens = []
    
    # Combine tokens from all fields with their sources and positions
    combined_tokens = []
    sources = []
    positions = []
    current_position = 0
    
    print("DEBUG: Combining tokens with position tracking...")
    
    # Add title tokens
    combined_tokens.extend(title_tokens)
    sources.extend(['T'] * len(title_tokens))
    positions.extend(list(range(current_position, current_position + len(title_tokens))))
    current_position += len(title_tokens)
    
    # Add text tokens
    combined_tokens.extend(text_tokens)
    sources.extend(['Te'] * len(text_tokens))
    positions.extend(list(range(current_position, current_position + len(text_tokens))))
    current_position += len(text_tokens)
    
    # Add tag tokens
    combined_tokens.extend(tags_tokens)
    sources.extend(['Ta'] * len(tags_tokens))
    positions.extend(list(range(current_position, current_position + len(tags_tokens))))
    current_position += len(tags_tokens)
    
    # Add author tokens
    combined_tokens.extend(authors_tokens)
    sources.extend(['A'] * len(authors_tokens))
    positions.extend(list(range(current_position, current_position + len(authors_tokens))))
    current_position += len(authors_tokens)
    
    print(f"DEBUG: Total combined tokens: {len(combined_tokens)}")
    return combined_tokens, sources, positions

def group_tokens_by_word(combined_tokens, sources, positions, lexicon, doc_id):
    """
    Group tokens by word and aggregate their data for inverted index
    """
    print(f"DEBUG: Grouping tokens by word for doc_id: {doc_id}")
    
    word_data = defaultdict(lambda: {'frequency': 0, 'positions': [], 'sources': []})
    
    tokens_in_lexicon = 0
    tokens_not_in_lexicon = 0
    
    for i, token in enumerate(combined_tokens):
        if token in lexicon:
            tokens_in_lexicon += 1
            word_data[token]['frequency'] += 1
            word_data[token]['positions'].append(positions[i])
            word_data[token]['sources'].append(sources[i])
        else:
            tokens_not_in_lexicon += 1
    
    print(f"DEBUG: Tokens in lexicon: {tokens_in_lexicon}")
    print(f"DEBUG: Tokens NOT in lexicon (will be skipped): {tokens_not_in_lexicon}")
    print(f"DEBUG: Unique words to process: {len(word_data)}")
    
    return word_data

def read_existing_row_data(inverted_index_folder, barrel_num, word_id):
    """
    Read existing data for a specific word_id from the barrel
    """
    print(f"DEBUG: Reading existing data for word_id {word_id} from barrel {barrel_num}")
    
    bin_file = f'{inverted_index_folder}/inverted_{barrel_num}.bin'
    csv_file = f'{inverted_index_folder}/inverted_{barrel_num}.csv'
    
    # Calculate position in barrel
    if word_id >= 1001:
        position = word_id % 1001 + 1
    else:
        position = word_id % 1001
    
    try:
        # Read offset information
        with open(bin_file, 'rb') as file:
            file.seek(8 * position)
            data = file.read(16)
            current_offset = struct.unpack('Q', data[:8])[0]
            next_offset = struct.unpack('Q', data[8:])[0]
        
        print(f"DEBUG: Word position {position}, offset range: {current_offset}-{next_offset}")
        
        # Read current row data
        with open(csv_file, 'rb') as file:
            file.seek(current_offset)
            content = file.read(next_offset - current_offset).decode().strip()
        
        if not content:
            print(f"DEBUG: No existing data found for word_id {word_id}")
            return None
        
        # Parse existing data
        csv_reader = csv.reader([content])
        row = next(csv_reader)
        
        existing_data = {
            'word_id': int(row[0]),
            'doc_ids': json.loads(row[1]),
            'frequencies': json.loads(row[2]),
            'positions': json.loads(row[3]),
            'sources': json.loads(re.sub("'", '"', row[4]))
        }
        
        print(f"DEBUG: Existing data has {len(existing_data['doc_ids'])} documents")
        return existing_data
        
    except FileNotFoundError as e:
        print(f"DEBUG: File not found error: {e}")
        return None
    except Exception as e:
        print(f"DEBUG: Error reading existing data: {e}")
        return None

def update_row_data(existing_data, word_id, doc_id, frequency, positions, sources):
    """
    Update existing row data with new document information
    """
    print(f"DEBUG: Updating row data for word_id {word_id}, doc_id {doc_id}")
    
    if existing_data is None:
        # Create new entry
        print("DEBUG: Creating new entry (no existing data)")
        return {
            'word_id': word_id,
            'doc_ids': [doc_id],
            'frequencies': [frequency],
            'positions': [positions],
            'sources': [sources]
        }
    
    # Check if document already exists
    if doc_id in existing_data['doc_ids']:
        print(f"DEBUG: Document {doc_id} already exists, updating...")
        doc_index = existing_data['doc_ids'].index(doc_id)
        existing_data['frequencies'][doc_index] = frequency
        existing_data['positions'][doc_index] = positions
        existing_data['sources'][doc_index] = sources
    else:
        print(f"DEBUG: Adding new document {doc_id} to existing entry")
        existing_data['doc_ids'].append(doc_id)
        existing_data['frequencies'].append(frequency)
        existing_data['positions'].append(positions)
        existing_data['sources'].append(sources)
    
    print(f"DEBUG: Updated entry now has {len(existing_data['doc_ids'])} documents")
    return existing_data

def update_csv_row_in_place(inverted_index_folder, barrel_num, word_id, updated_data):
    """
    Update a specific row in the CSV file by rewriting the entire file
    """
    print(f"DEBUG: Updating CSV row for barrel {barrel_num}, word_id {word_id}")
    
    csv_file = f'{inverted_index_folder}/inverted_{barrel_num}.csv'
    temp_file = f'{csv_file}.tmp'
    
    # Calculate position in barrel for the word
    if word_id >= 1001:
        target_position = word_id % 1001 + 1
    else:
        target_position = word_id % 1001
    
    try:
        # Read all existing data and update the specific row
        updated_rows = []
        found_target = False
        
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader, None)  # Read header
            if header:
                updated_rows.append(header)
            
            current_row = 0
            for row in reader:
                current_row += 1
                if len(row) >= 5:
                    existing_word_id = int(row[0])
                    
                    if existing_word_id == word_id:
                        print(f"DEBUG: Found target word_id {word_id} at row {current_row}")
                        # Replace with updated data
                        new_row = [
                            updated_data['word_id'],
                            json.dumps(updated_data['doc_ids']),
                            json.dumps(updated_data['frequencies']),
                            json.dumps(updated_data['positions']),
                            json.dumps(updated_data['sources'])
                        ]
                        updated_rows.append(new_row)
                        found_target = True
                    else:
                        # Keep existing row
                        updated_rows.append(row)
                else:
                    updated_rows.append(row)
        
        # If word_id wasn't found, add it as a new row
        if not found_target:
            print(f"DEBUG: Word_id {word_id} not found, adding as new row")
            new_row = [
                updated_data['word_id'],
                json.dumps(updated_data['doc_ids']),
                json.dumps(updated_data['frequencies']),
                json.dumps(updated_data['positions']),
                json.dumps(updated_data['sources'])
            ]
            updated_rows.append(new_row)
        
        # Write updated data to temporary file
        with open(temp_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(updated_rows)
        
        # Replace original file with updated file
        shutil.move(temp_file, csv_file)
        print(f"DEBUG: Successfully updated CSV file with {len(updated_rows)-1} data rows")
        
    except Exception as e:
        print(f"DEBUG: Error updating CSV row: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise

def recreate_barrel_offsets(inverted_index_folder, barrel_num):
    """
    Recreate the offsets file for a barrel after updating CSV
    """
    print(f"DEBUG: Recreating offsets for barrel {barrel_num}")
    
    csv_file = f'{inverted_index_folder}/inverted_{barrel_num}.csv'
    bin_file = f'{inverted_index_folder}/inverted_{barrel_num}.bin'
    
    try:
        offsets = []
        with open(csv_file, 'r', encoding='utf-8') as file:
            while True:
                offset = file.tell()
                line = file.readline()
                if not line:
                    break
                offsets.append(offset)
        
        # Save offsets to binary file
        with open(bin_file, 'wb') as offset_file:
            for offset in offsets:
                offset_file.write(struct.pack('Q', offset))
        
        print(f"DEBUG: Successfully recreated offsets file with {len(offsets)} entries")
        
    except Exception as e:
        print(f"DEBUG: Error recreating offsets: {e}")
        raise

def update_inverted_index_with_article(article_data, doc_id, lexicon, inverted_index_folder, stop_words):
    """
    Main function to process scraped article and update inverted index
    """
    print(f"DEBUG: Starting inverted index update for doc_id {doc_id}")
    print(f"DEBUG: Article title: {article_data['title'][:50]}...")
    
    # Process article tokens
    combined_tokens, sources, positions = process_scraped_article_tokens(article_data, stop_words)
    
    if not combined_tokens:
        print("DEBUG: No tokens found, skipping index update")
        return False
    
    # Group tokens by word
    word_data = group_tokens_by_word(combined_tokens, sources, positions, lexicon, doc_id)
    
    if not word_data:
        print("DEBUG: No words found in lexicon, skipping index update")
        return False
    
    # Batch updates per barrel
    barrel_updates = defaultdict(dict)  # barrel_num -> {word_id: updated_data}
    for word, data in word_data.items():
        try:
            word_id = lexicon[word]
            barrel_num = word_id // 1001
            print(f"DEBUG: Processing word '{word}' (ID: {word_id}, Barrel: {barrel_num})")
            print(f"DEBUG: Word frequency: {data['frequency']}, positions: {len(data['positions'])}")
            # Read existing data for this word
            existing_data = read_existing_row_data(inverted_index_folder, barrel_num, word_id)
            # Update the data
            updated_data = update_row_data(
                existing_data, word_id, doc_id,
                data['frequency'], data['positions'], data['sources']
            )
            barrel_updates[barrel_num][word_id] = updated_data
        except KeyError:
            print(f"DEBUG: Word '{word}' not found in lexicon, skipping")
        except Exception as e:
            print(f"DEBUG: Error processing word '{word}': {e}")
            continue

    # Update each barrel file only once
    print(f"DEBUG: Updating {len(barrel_updates)} barrels in batch mode...")
    for barrel_num, updates in barrel_updates.items():
        try:
            # Read all existing rows
            csv_file = f'{inverted_index_folder}/inverted_{barrel_num}.csv'
            temp_file = f'{csv_file}.tmp'
            updated_rows = []
            found_word_ids = set()
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader, None)
                if header:
                    updated_rows.append(header)
                for row in reader:
                    if len(row) >= 5:
                        existing_word_id = int(row[0])
                        if existing_word_id in updates:
                            # Replace with updated data
                            new_row = [
                                updates[existing_word_id]['word_id'],
                                json.dumps(updates[existing_word_id]['doc_ids']),
                                json.dumps(updates[existing_word_id]['frequencies']),
                                json.dumps(updates[existing_word_id]['positions']),
                                json.dumps(updates[existing_word_id]['sources'])
                            ]
                            updated_rows.append(new_row)
                            found_word_ids.add(existing_word_id)
                        else:
                            updated_rows.append(row)
                    else:
                        updated_rows.append(row)
            # Add new word_ids not found in file
            for word_id, updated_data in updates.items():
                if word_id not in found_word_ids:
                    print(f"DEBUG: Word_id {word_id} not found, adding as new row")
                    new_row = [
                        updated_data['word_id'],
                        json.dumps(updated_data['doc_ids']),
                        json.dumps(updated_data['frequencies']),
                        json.dumps(updated_data['positions']),
                        json.dumps(updated_data['sources'])
                    ]
                    updated_rows.append(new_row)
            # Write updated data to temporary file
            with open(temp_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(updated_rows)
            # Replace original file with updated file
            shutil.move(temp_file, csv_file)
            print(f"DEBUG: Successfully updated CSV file for barrel {barrel_num} with {len(updated_rows)-1} data rows")
            # Recreate offsets for barrel
            recreate_barrel_offsets(inverted_index_folder, barrel_num)
        except Exception as e:
            print(f"DEBUG: Error updating barrel {barrel_num}: {e}")
    print(f"DEBUG: Successfully completed inverted index update")
    print(f"DEBUG: Updated {len(word_data)} unique words across {len(barrel_updates)} barrels")
    return True

def add_scraped_article_to_index(article_data, doc_id, lexicon, inverted_index_folder, stop_words):
    """
    Convenience function to add a scraped article to the inverted index
    
    Args:
        article_data: Dict containing scraped article data
        doc_id: Document ID for this article
        lexicon: Dictionary mapping words to word IDs
        inverted_index_folder: Path to inverted index folder
        stop_words: Set of stop words to filter out
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        return update_inverted_index_with_article(
            article_data, doc_id, lexicon, inverted_index_folder, stop_words
        )
    except Exception as e:
        print(f"DEBUG: Failed to add article to index: {e}")
        return False