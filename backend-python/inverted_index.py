import csv
import os
import struct
from forward_index import load_forward_barrel
from config import inverted_index_folder

def save_inverted_barrel(inverted_barrel, file_name):
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if os.stat(file_name).st_size == 0:  # Check if file is empty
            writer.writerow(['WordID', 'DocIDs', 'Frequencies', 'Positions', 'Sources'])
                
        inverted_entries = []
        for word_id in list(inverted_barrel.keys()):
            doc_ids = list(inverted_barrel[word_id].keys())
            frequencies = []
            positions = []
            sources = []
            for doc_id in doc_ids:
                frequencies.append(inverted_barrel[word_id][doc_id][0])
                positions.append(inverted_barrel[word_id][doc_id][1])
                sources.append(inverted_barrel[word_id][doc_id][2])
            inverted_entries.append([word_id, doc_ids, frequencies, positions, sources])
            del inverted_barrel[word_id]
            
        writer.writerows(inverted_entries)



def update_inverted_barrel(forward_barrel_file, inverted_barrel_file):
    os.makedirs(inverted_index_folder, exist_ok=True)
    # Load the forward index
    forward_barrel = load_forward_barrel(forward_barrel_file)

    # Load the existing inverted index
    inverted_barrel = {}
    
    for doc_id in forward_barrel:
        for i in range(len(forward_barrel[doc_id][0])):
            word_id = forward_barrel[doc_id][0][i]
            if word_id not in inverted_barrel:
                inverted_barrel[word_id] = {}
            inverted_barrel[word_id][doc_id] = [forward_barrel[doc_id][1][i], forward_barrel[doc_id][2][i], forward_barrel[doc_id][3][i]]
    
    # Save only new data to the CSV file
    save_inverted_barrel(inverted_barrel, inverted_barrel_file)
    print(f"Inverted barrel {inverted_barrel_file} has been updated and saved.")


def create_offsets(inverted_index_folder, barrel_number):
    offsets = []
    with open(inverted_index_folder + f'/inverted_{barrel_number}.csv', mode='r', encoding='utf-8') as file:
        while True:
            offset = file.tell()
            line = file.readline()
            if not line:
                break
            offsets.append(offset)

    # Save offsets to a binary file
    with open(inverted_index_folder + f'/inverted_{barrel_number}.bin', mode='wb') as offset_file:
        for offset in offsets:
            offset_file.write(struct.pack('Q', offset))


def load_offsets(file_name):
    offsets = []
    with open(file_name, mode='rb') as offset_file:
        while True:
            bytes_read = offset_file.read(8)
            if not bytes_read:
                break
            offsets.append(struct.unpack('Q', bytes_read)[0])
    return offsets