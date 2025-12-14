from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import aiofiles # type: ignore
import struct
import csv
import json
import re
import os
import asyncio

# 08: Interfaces & Subtyping
class IndexReader(ABC):
    """
    Interface for reading inverted index data.
    """
    @abstractmethod
    async def get_word_data(self, word: str, word_id: int) -> Optional[Dict[str, Any]]:
        pass

class FileIndexReader(IndexReader):
    """
    Implementation of IndexReader that reads from files.
    """
    def __init__(self, inverted_index_folder: str):
        self.inverted_index_folder = inverted_index_folder

    # 14: Concurrency (Async/Await)
    async def get_word_data(self, word: str, word_id: int) -> Optional[Dict[str, Any]]:
        try:
            barrel = word_id // 1001
            if word_id >= 1001:
                position_idx = word_id % 1001 + 1
            else:
                position_idx = word_id % 1001
            
            # Async file reading
            bin_path = f'{self.inverted_index_folder}/inverted_{barrel}.bin'
            csv_path = f'{self.inverted_index_folder}/inverted_{barrel}.csv'

            if not os.path.exists(bin_path) or not os.path.exists(csv_path):
                return None

            async with aiofiles.open(bin_path, 'rb') as file:
                await file.seek(8 * position_idx)
                data = await file.read(16)
                if not data:
                    return None
                start_pos = struct.unpack('Q', data[:8])[0]
                end_pos = struct.unpack('Q', data[8:])[0]

            async with aiofiles.open(csv_path, 'rb') as file:
                await file.seek(start_pos)
                content_bytes = await file.read(end_pos - start_pos)
                content = content_bytes.decode()
                
            # Parsing CSV line
            # Since we read a specific chunk, it should be a single line or part of it.
            # The original code used csv.reader on the string.
            csv_reader = csv.reader([content])
            for row in csv_reader:
                # row structure: WordID, DocIDs, Frequencies, Positions, Sources
                doc_ids = json.loads(row[1])
                frequencies = json.loads(row[2])
                positions = json.loads(row[3])
                types_str = re.sub("'", '"', row[4])
                types = json.loads(types_str)
                
                return {
                    'doc_ids': doc_ids,
                    'frequencies': frequencies,
                    'positions': positions,
                    'types': types
                }
        except Exception as e:
            print(f'Error processing word {word}: {e}')
            return None
        return None
