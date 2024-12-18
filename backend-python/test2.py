from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from lexicon_utils import load_lexicon, preprocess_word
from inverted_index import load_offsets
from config import inverted_index_folder, lexicon_file, processed_file
from csv_utils import load_processed_to_dict
from nltk.tokenize import word_tokenize
from nltk import WordNetLemmatizer
import struct
import csv
import json
import re

app = FastAPI()
lexicon = load_lexicon(lexicon_file)
processed_dict = load_processed_to_dict(processed_file)
lemmatizer = WordNetLemmatizer()
preprocess_word('apple')
csv.field_size_limit(100_000_000)

# Enable CORS to allow requests from your Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request body structure
class QueryRequest(BaseModel):
    query: str

# Define the response structure
class SearchResult(BaseModel):
    id: int
    title: str
    description: str
    thumbnail: str
    url: str
    tags: List[str]
    date: str

@app.post("/search", response_model=List[SearchResult])
def search_documents(request: QueryRequest):
    query = request.query.lower()

    results = []

    query = word_tokenize(query)
    query = [preprocess_word(word) for word in query if preprocess_word(word)]  # Preprocess each word in the query
    # query = [lemmatizer.lemmatize(query, pos="v")]
    for word in query:
        try:
            word_id = lexicon[word]
            barrel = word_id // 1001
            position = word_id % 1001 + 1
            print(word)
            
            with open(inverted_index_folder + f'/inverted_{barrel}.bin', 'rb') as file:
                file.seek(8 * position)
                data = file.read(16)
                position = struct.unpack('Q', data[:8])[0]
                next_position = struct.unpack('Q', data[8:])[0]
                
            with open(inverted_index_folder + f'/inverted_{barrel}.csv', 'rb') as file:
                file.seek(position)
                content = file.read(next_position - position).decode()
                
            csv_reader = csv.reader([content])  # Treat line as a single CSV row
            for row in csv_reader:
                word_id = int(row[0])  # First column is the word ID
                doc_ids = json.loads(row[1])  # Second column: Document IDs (JSON array)
                frequencies = json.loads(row[2])  # Third column: Frequencies
                positions = json.loads(row[3])  # Fourth column: Positions
                types = re.sub('\'', '"', row[4])
                types = json.loads(types)  # Fifth column: Types (title, tags, etc.)
            
            doc_frequency_pairs = list(zip(doc_ids, frequencies))
            sorted_doc_frequency_pairs = sorted(doc_frequency_pairs, key=lambda x: x[1], reverse=True)
            top_5_documents = sorted_doc_frequency_pairs[:5]
            
            for doc_ids, frequencies in top_5_documents:
                processed_data = processed_dict[doc_ids]
                results.append({
                    "id": doc_ids,
                    "title": processed_data['title'],
                    "description": "Placeholder description",
                    "thumbnail": "Placeholder thumbnail",
                    "url": processed_data['url'],
                    "tags": processed_data['tags'],
                    "date": processed_data['timestamp']
                })
            
        except (KeyError):
            print(f'Word {word} not in Lexicon')

    
    return results