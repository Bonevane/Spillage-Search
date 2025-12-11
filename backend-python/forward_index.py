import re
import csv
import os
import json
from typing import Dict, List, Any, Union, Optional
from pathlib import Path

# Type definitions
DocID = int
WordID = int
Frequency = int
Position = int
Source = str

# The structure loaded from CSV: [WordIDs, Frequencies, Positions, Sources]
LoadedForwardData = List[Union[List[WordID], List[Frequency], List[List[Position]], List[List[Source]]]]
ForwardBarrel = Dict[DocID, LoadedForwardData]

# The structure used during indexing before saving
WordData = Dict[str, Any] # keys: 'frequency', 'positions', 'sources'
InMemoryBarrel = Dict[DocID, Dict[WordID, WordData]]
ForwardIndex = List[InMemoryBarrel]


def load_forward_barrel(file_name: str) -> ForwardBarrel:
    """
    Load existing forward index from a file.
    
    Args:
        file_name: The path to the forward barrel CSV file.
        
    Returns:
        A dictionary mapping DocID to a list containing [WordIDs, Frequencies, Positions, Sources].
        Returns an empty dictionary if the file does not exist.
    """
    forward_barrel: ForwardBarrel = {}
    file_path = Path(file_name)
    
    if file_path.exists():
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if not row['DocID']:
                    continue
                    
                doc_id = int(row['DocID'])
                word_ids: List[WordID] = json.loads(row['WordIDs'])
                frequencies: List[Frequency] = json.loads(row['Frequencies'])
                positions: List[List[Position]] = json.loads(row['Positions'])
                
                # Handle potential single quotes in JSON string for sources
                sources_str = re.sub('\'', '"', row['Sources'])
                sources: List[List[Source]] = json.loads(sources_str)
                
                forward_barrel[doc_id] = [word_ids, frequencies, positions, sources]
                
    return forward_barrel


def save_forward_index(forward_index: ForwardIndex, folder_name: str) -> None:
    """
    Save the in-memory forward index to CSV files.
    
    Args:
        forward_index: A list of dictionaries, where each dictionary represents a barrel.
        folder_name: The directory to save the files in.
    """
    folder_path = Path(folder_name)
    folder_path.mkdir(parents=True, exist_ok=True)
    
    for barrel_idx, barrel_data in enumerate(forward_index):
        if not barrel_data:
            continue
            
        file_name = folder_path / f"forward_{barrel_idx}.csv"
        
        # Check if file exists and is empty to decide whether to write header
        file_exists = file_name.exists()
        is_empty = file_exists and file_name.stat().st_size == 0
        
        mode = 'a' if file_exists else 'w'
        
        with open(file_name, mode=mode, newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write the header if creating new file or appending to empty file
            if not file_exists or is_empty:
                writer.writerow(['DocID', 'WordIDs', 'Frequencies', 'Positions', 'Sources'])
            
            forward_entries = []
            for doc_id, word_data_map in barrel_data.items():
                # Extract WordIDs, Frequencies, Positions, and Sources
                word_ids = list(word_data_map.keys())
                frequencies = [data['frequency'] for data in word_data_map.values()]
                positions = [data['positions'] for data in word_data_map.values()]
                sources = [data['sources'] for data in word_data_map.values()]
                
                forward_entries.append([doc_id, word_ids, frequencies, positions, sources])
                
            writer.writerows(forward_entries)