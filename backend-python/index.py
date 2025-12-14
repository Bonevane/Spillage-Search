import csv
import os
import re
import ast
import time as t
from typing import List, Dict, Set, Tuple, Any, Optional
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from config import (
    id_file, 
    doc_id_file, 
    processed_file, 
    forward_index_folder, 
    inverted_index_folder,
    lexicon_file
)
from csv_utils import load_latest_id, load_latest_doc_id, save_processed_docs, load_processed_entries
from lexicon_utils import load_lexicon, preprocess_word, save_words_to_lexicon
from forward_index import save_forward_index
from inverted_index import update_inverted_barrel, create_offsets
from classes import WordDataEntry

class DatasetIndexer:
    """
    Class responsible for indexing a dataset into forward indices.
    
    Attributes:
        dataset_file (str): Path to the dataset CSV file.
        lexicon_file (str): Path to the lexicon CSV file.
        stop_words (Set[str]): Set of stop words to ignore.
        processed_set (Set[Tuple[Any, ...]]): Set of already processed documents.
        lexicon (Dict[str, int]): Mapping of words to word IDs.
        latest_doc_id (int): The ID of the last processed document.
        latest_id (int): The ID of the last assigned word ID.
        lexicon_entries (List[List[Any]]): New entries to be added to the lexicon.
        forward_entries (List[Dict[int, Dict[int, WordDataEntry]]]): Forward index data.
    """
    BARREL_SIZE = 1001

    def __init__(self, dataset_file: str, lexicon_file: str):
        self.dataset_file = dataset_file
        self.lexicon_file = lexicon_file
        self.stop_words: Set[str] = set(stopwords.words('english'))
        self.processed_set: Set[Tuple[Any, ...]] = load_processed_entries()
        self.lexicon: Dict[str, int] = load_lexicon(lexicon_file)
        self.latest_doc_id: int = load_latest_doc_id()
        self.latest_id: int = load_latest_id()
        self.lexicon_entries: List[List[Any]] = []
        self.forward_entries: List[Dict[int, Dict[int, WordDataEntry]]] = []

    def iterate_dataset(self) -> None:
        """
        Iterates through the dataset and indexes new documents.
        """
        with open(self.dataset_file, mode='r', encoding='utf-8') as file:    
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                # Check if the current document has already been processed
                # Note: row values are strings.
                current_entry = (row['title'], row['url'], row['authors'], row['timestamp'], row['tags'])
                if current_entry in self.processed_set:
                    continue
                
                self._index_dataset_row(row)

                # Mark the document as processed and save it
                self.processed_set.add(current_entry)
                # TODO: Refactor save_processed_docs to take a cleaner input or use ArticleData
                save_processed_docs([[
                    self.latest_doc_id, 
                    row['title'], 
                    row['url'], 
                    row['authors'], 
                    row['timestamp'], 
                    row['tags']
                ]], self.latest_doc_id)
                
                if self.latest_doc_id % self.BARREL_SIZE == 0:
                    self._save_batch()
            
            # Save remaining
            if self.forward_entries:
                self._save_batch(final=True)

    def _save_batch(self, final: bool = False) -> None:
        save_words_to_lexicon(self.lexicon, self.lexicon_entries, self.latest_id)
        save_forward_index(self.forward_entries, forward_index_folder)
        self.lexicon_entries.clear()
        
        start_batch = self.latest_doc_id - (self.latest_doc_id % self.BARREL_SIZE) if final else self.latest_doc_id - self.BARREL_SIZE
        print(f"Writing batch {start_batch} to {self.latest_doc_id}...")
        
        if not final:
             self.forward_entries.clear()

    def _process_tokens(self, current_position: int, tokens: List[str], combined_tokens: List[str], sources: List[str], positions: List[int], type_code: str) -> int:
        combined_tokens.extend(tokens)
        sources.extend([type_code] * len(tokens))
        positions.extend(list(range(current_position, current_position + len(tokens))))
        return current_position + len(tokens)

    def _index_dataset_row(self, row: Dict[str, str]) -> None:
        pattern = r'[^A-Za-z0-9 ]+'
        
        # Process fields
        title_tokens = self._tokenize_and_clean(row['title'], pattern)
        
        text_tokens: List[str] = []
        if 'text' in row:
             for paragraph in row['text'].split("\n"):
                text_tokens.extend(self._tokenize_and_clean(paragraph, pattern))
        
        tags_tokens: List[str] = []
        authors_tokens: List[str] = []
        try:
            # Handle tags
            tags_list = ast.literal_eval(row['tags'])
            for tag in tags_list:
                tags_tokens.extend(self._tokenize_and_clean(tag, pattern))
            
            # Handle authors
            authors_list = ast.literal_eval(row['authors'])
            for author in authors_list:
                authors_tokens.extend(self._tokenize_and_clean(author, pattern))
        except (ValueError, SyntaxError):   
            print(f"Skipping row due to invalid tags/authors format: {row.get('tags', '')}")

        # Combine tokens
        combined_tokens: List[str] = []
        sources: List[str] = []
        positions: List[int] = []
        current_position = 0
        
        current_position = self._process_tokens(current_position, title_tokens, combined_tokens, sources, positions, 'T')
        current_position = self._process_tokens(current_position, text_tokens, combined_tokens, sources, positions, 'Te')
        current_position = self._process_tokens(current_position, tags_tokens, combined_tokens, sources, positions, 'Ta')
        current_position = self._process_tokens(current_position, authors_tokens, combined_tokens, sources, positions, 'A')

        self.latest_doc_id += 1

        # Update Forward Index
        for position, (token, source) in enumerate(zip(combined_tokens, sources)):
            if token not in self.lexicon:
                self.latest_id += 1
                self.lexicon[token] = self.latest_id
                self.lexicon_entries.append([self.latest_id, token])
            
            word_id = self.lexicon[token]
            barrel = word_id // self.BARREL_SIZE
            
            # Ensure forward_entries has enough barrels
            while len(self.forward_entries) <= barrel:
                self.forward_entries.append({})
            
            # Ensure doc_id exists in barrel
            if self.latest_doc_id not in self.forward_entries[barrel]:
                self.forward_entries[barrel][self.latest_doc_id] = {}
            
            # Add token data
            if word_id not in self.forward_entries[barrel][self.latest_doc_id]:
                self.forward_entries[barrel][self.latest_doc_id][word_id] = {
                    "frequency": 0, 
                    "positions": [], 
                    "sources": []
                }
            
            entry = self.forward_entries[barrel][self.latest_doc_id][word_id]
            entry["frequency"] += 1
            entry["positions"].append(position)
            entry["sources"].append(source)

    def _tokenize_and_clean(self, text: str, pattern: str) -> List[str]:
        tokens = [preprocess_word(token) for token in word_tokenize(re.sub(pattern, ' ', text))]
        return [w for w in tokens if w.lower() not in self.stop_words and len(w) > 2]

class InvertedIndexBuilder:
    """
    Class responsible for creating inverted indices from forward indices.
    """
    @staticmethod
    def create_inverted_index() -> None:
        barrel = 0
        while True:
            forward_file = os.path.join(forward_index_folder, f'forward_{barrel}.csv')
            if os.path.isfile(forward_file):
                print(f"Creating inverted barrel {barrel}...")
                inverted_file = os.path.join(inverted_index_folder, f'inverted_{barrel}.csv')
                update_inverted_barrel(forward_file, inverted_file)
                create_offsets(inverted_index_folder, barrel)
                barrel += 1
            else:
                break

# Backward compatibility functions
def iterate_dataset(dataset_file: str, lexicon_file: str) -> None:
    indexer = DatasetIndexer(dataset_file, lexicon_file)
    indexer.iterate_dataset()

def create_inverted_index() -> None:
    InvertedIndexBuilder.create_inverted_index()
