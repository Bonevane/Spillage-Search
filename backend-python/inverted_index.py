import csv
import os
import struct
from typing import Dict, List, Any, Union
from pathlib import Path
from forward_index import load_forward_barrel
from config import inverted_index_folder

# Type aliases
WordID = int
DocID = int
Frequency = int
Position = int
Source = str
InvertedEntry = List[Union[WordID, List[DocID], List[Frequency], List[List[Position]], List[List[Source]]]]
InvertedBarrel = Dict[WordID, Dict[DocID, List[Any]]]

def save_inverted_barrel(inverted_barrel: InvertedBarrel, file_name: str) -> None:
    """
    Save an inverted barrel to a CSV file.
    
    Args:
        inverted_barrel: The inverted barrel data structure.
        file_name: The path to the file to save to.
    """
    file_path = Path(file_name)
    # Check if file exists and is not empty to determine mode
    mode = 'a' if file_path.exists() and file_path.stat().st_size > 0 else 'w'
    
    with open(file_path, mode=mode, newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if mode == 'w':
            writer.writerow(['WordID', 'DocIDs', 'Frequencies', 'Positions', 'Sources'])
                
        inverted_entries: List[List[Any]] = []
        # Note: Modifying the dictionary while iterating is generally unsafe, 
        # but here we are creating a list and then deleting keys.
        # Better to iterate over a copy of keys.
        for word_id in list(inverted_barrel.keys()):
            doc_ids = list(inverted_barrel[word_id].keys())
            frequencies: List[int] = []
            positions: List[List[int]] = []
            sources: List[List[str]] = []
            
            for doc_id in doc_ids:
                data = inverted_barrel[word_id][doc_id]
                frequencies.append(data[0])
                positions.append(data[1])
                sources.append(data[2])
                
            inverted_entries.append([word_id, doc_ids, frequencies, positions, sources])
            del inverted_barrel[word_id]
            
        writer.writerows(inverted_entries)


def update_inverted_barrel(forward_barrel_file: str, inverted_barrel_file: str) -> None:
    """
    Create or update an inverted barrel from a forward barrel.
    
    Args:
        forward_barrel_file: Path to the forward barrel file.
        inverted_barrel_file: Path to the inverted barrel file.
    """
    os.makedirs(inverted_index_folder, exist_ok=True)
    
    # Load the forward barrel
    forward_barrel = load_forward_barrel(forward_barrel_file)

    # Initialization
    inverted_barrel: InvertedBarrel = {}
    
    for doc_id, data in forward_barrel.items():
        word_ids = data[0]
        frequencies = data[1]
        positions = data[2]
        sources = data[3]
        
        for i in range(len(word_ids)):
            word_id = word_ids[i]
            if word_id not in inverted_barrel:
                inverted_barrel[word_id] = {}
            
            inverted_barrel[word_id][doc_id] = [
                frequencies[i], 
                positions[i], 
                sources[i]
            ]
    
    # Save only new data to the CSV file
    save_inverted_barrel(inverted_barrel, inverted_barrel_file)
    print(f"Inverted barrel {inverted_barrel_file} has been updated and saved.")



def create_offsets(inverted_index_folder_path: str, barrel_number: int) -> None:
    """
    Create offsets for an inverted barrel CSV file and save them to a binary file.
    
    Args:
        inverted_index_folder_path: Path to the folder containing inverted indexes.
        barrel_number: The number of the barrel to process.
    """
    folder = Path(inverted_index_folder_path)
    csv_file = folder / f'inverted_{barrel_number}.csv'
    bin_file = folder / f'inverted_{barrel_number}.bin'
    
    offsets: List[int] = []
    
    if not csv_file.exists():
        print(f"Warning: {csv_file} does not exist.")
        return

    with open(csv_file, mode='r', encoding='utf-8') as file:
        while True:
            offset = file.tell()
            line = file.readline()
            if not line:
                break
            offsets.append(offset)

    # Save offsets to a binary file
    with open(bin_file, mode='wb') as offset_file:
        for offset in offsets:
            offset_file.write(struct.pack('Q', offset))


def load_offsets(file_name: str) -> List[int]:
    """
    Load offsets from a binary file.
    
    Args:
        file_name: Path to the binary offsets file.
        
    Returns:
        A list of file offsets.
    """
    offsets: List[int] = []
    file_path = Path(file_name)
    
    if not file_path.exists():
        return offsets
        
    with open(file_path, mode='rb') as offset_file:
        while True:
            bytes_read = offset_file.read(8)
            if not bytes_read:
                break
            offsets.append(struct.unpack('Q', bytes_read)[0])
    return offsets