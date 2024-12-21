from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from concurrent.futures import ProcessPoolExecutor
from nltk.tokenize import word_tokenize
from nltk import WordNetLemmatizer
from sentence_transformers import SentenceTransformer, util
from sortedcontainers import SortedList
import numpy as np
from pydantic import BaseModel
from typing import List

from lexicon_utils import load_lexicon, preprocess_word
from inverted_index import load_offsets
from index import iterate_dataset, create_inverted_index
from config import inverted_index_folder, lexicon_file, processed_file, scrapped_file, received_file, lengths_file
from csv_utils import load_processed_to_dict, load_scrapped_to_dict, load_lengths

import threading
import struct
import csv
import json
import re
import io
import os
import math
import time as t
import torch
import uvicorn

app = FastAPI()

port = int(os.getenv("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)

# Loading transformer model and vocab embeddings
# vocab_embeddings = np.load("embeddings.npy")
# print("Model and embeddings loaded successfully.")

# Loading lexicon, processed data, scrapped data and lengths data
lexicon = load_lexicon(lexicon_file)
vocab = list(lexicon.keys())
processed_dict = load_processed_to_dict(processed_file)
scrapped_dict = load_scrapped_to_dict(scrapped_file)
lengths_dict = load_lengths(lengths_file)

k = 1.5
b = 0.75
N = 192000
avgdl = sum(lengths_dict.values()) / N

# Loading lemmatizer and intializing it (For some reason it takes too long to lemmatize the first time)
lemmatizer = WordNetLemmatizer()
preprocess_word('apple')

# Increase the field size limit to read larger CSV rows
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
    member: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a JSON file.")

    try:
        contents = await file.read()
        data = json.loads(contents)
        
        required_keys = ['title', 'text', 'url', 'authors', 'timestamp', 'tags']
        if not all(key in data for key in required_keys):
            raise HTTPException(status_code=400, detail="Invalid JSON structure. Missing required keys.")
        
        # Convert JSON to CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=required_keys)
        writer.writeheader()
        writer.writerow(data)
        csv_content = output.getvalue()
        output.close()
        
        # Save CSV to a file or pass it to a function
        with open(received_file, 'w', newline='', encoding='utf-8') as csvfile:
            csvfile.write(csv_content)

        iterate_dataset(received_file, lexicon_file)

        executor = ProcessPoolExecutor()
        executor.submit(create_inverted_index)
        
        if os.path.exists(received_file):
            os.remove(received_file)
            print(f"CSV file {received_file} deleted.")
        
        print("Received JSON data:", data)
        return JSONResponse(content={"message": "File uploaded successfully!", "data": data})
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file.")


def append_inverted_barrel_data(lexicon, inverted_index_folder, word, data_dict):
    try:
        word_id = lexicon[word]
        barrel = word_id // 1001
        if word_id >= 1001:
            position = word_id % 1001 + 1
        else:
            position = word_id % 1001
        print(f"Processing word: {word}")

        with open(f'{inverted_index_folder}/inverted_{barrel}.bin', 'rb') as file:
            file.seek(8 * position)
            data = file.read(16)
            position = struct.unpack('Q', data[:8])[0]
            next_position = struct.unpack('Q', data[8:])[0]

        with open(f'{inverted_index_folder}/inverted_{barrel}.csv', 'rb') as file:
            file.seek(position)
            content = file.read(next_position - position).decode()
            
        csv_reader = csv.reader([content])  # Treat line as a single CSV row
        for row in csv_reader:
            word_id = int(row[0])  # First column is the word ID
            doc_ids = json.loads(row[1])  # Second column: Document IDs (JSON array)
            frequencies = json.loads(row[2])  # Third column: Frequencies
            positions = json.loads(row[3])  # Fourth column: Positions
            types = re.sub("'", '"', row[4])
            types = json.loads(types)  # Fifth column: Types (title, tags, etc.)
            
            data_dict[word_id] = {
                'doc_ids': doc_ids,
                'frequencies': frequencies,
                'positions': positions,
                'types': types
            }
    except KeyError:
        print(f'Word {word} not in Lexicon')
    except Exception as e:
        print(f'Error processing word {word}: {e}')


def calculate_bm25_scores(item, sorted_list, query_word_ids, intersection):
    word_id, data = item
    doc_ids = data['doc_ids']
    frequencies = data['frequencies']
    sources = data['types']
    
    # Calculate IDF
    n = len(doc_ids)  # Number of documents containing the term
    IDF = math.log10((N - n + 0.5) / (n + 0.5))
    
    # Calculate BM25 scores for each document
    for doc_id, frequency, source in zip(doc_ids, frequencies, sources):
        length = lengths_dict[doc_id]  # Length of the document
        TF = frequency / (frequency + k * (1 - b + b * length / avgdl))
        score = TF * IDF * 100
        
        if doc_id in intersection:
            score *= 10
        
        if word_id in query_word_ids:
            score *= 3
        
        if "T" in source: 
            score *= 10
        if "A" in source:
            score *= 12
        if "Ta" in source:
            score *= 8
        
        sorted_list.add((score, doc_id))

def get_top_words_from_query(query):
    all_top_words = []
    query_embeddings = []
    for word in query:
        word_id = lexicon[word]
        query_embeddings.append(vocab_embeddings[word_id - 1])

    similarities = util.cos_sim(query_embeddings, vocab_embeddings)  # shape: (len(query), len(vocab))
    
    for idx, q_word in enumerate(query):
        row = similarities[idx]
        top_values, top_indices = torch.topk(row, 5)
        all_top_words.extend([vocab[i] for i in top_indices])
        
    return all_top_words

def find_intersection(inverted_data, query_word_ids):    
    if not query_word_ids:
        return set()  # Return an empty set if no valid word IDs are found

    # Find the intersection of document IDs
    for word_id in query_word_ids:
        if word_id in inverted_data:
            doc_ids = set(inverted_data[word_id]['doc_ids'])
            break
    else:
        return set()
    
    for word_id in query_word_ids:
        if word_id in inverted_data:
            doc_ids &= set(inverted_data[word_id]['doc_ids'])
    
    return doc_ids


def make_results(sorted_list, results):
    counter = 0
    processed_doc_ids = set()
    for score, doc_ids in sorted_list[::-1]:
        if doc_ids in processed_doc_ids:
            continue  # Skip duplicate entries
        processed_doc_ids.add(doc_ids)
        
        processed_data = processed_dict[doc_ids]
        
        description = "Placeholder description"
        thumbnail = "Placeholder thumbnail"
        member = "No"
        
        try:
            description = scrapped_dict[int(doc_ids)]['description']
            thumbnail = scrapped_dict[int(doc_ids)]['url']
            member = scrapped_dict[int(doc_ids)]['member only']
            if member == "Unknown":
                continue
        except (Exception):
            pass
        
        results.append({
            "id": doc_ids,
            "title": processed_data['title'],
            "description": description,
            "thumbnail": thumbnail,
            "url": processed_data['url'],
            "tags": processed_data['tags'],
            "date": processed_data['timestamp'],
            "member" : member
        })
        
        counter += 1  # Increment the counter
        if counter >= 30:
            break


@app.post("/search", response_model=List[SearchResult])
def search_documents(request: QueryRequest):
    a = t.time()
    query = request.query.lower()

    results = []
    bm25_scores = []
    inverted_data = {}
    sorted_list = SortedList()

    query = word_tokenize(query)
    query = list(set(query))
    query = [preprocess_word(word) for word in query if preprocess_word(word) in lexicon]  # Preprocess each word in the query
    query_word_ids = [lexicon[word] for word in query if word in lexicon]
    
    if not query:
        return results
    
    # top_words_list = get_top_words_from_query(query)
    top_words_list = query

    threads = []
    for word in top_words_list:
        thread = threading.Thread(target=append_inverted_barrel_data, args=(lexicon, inverted_index_folder, word, inverted_data))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    intersection = find_intersection(inverted_data, query_word_ids)
    
    bm25_threads = []
    for item in inverted_data.items():
        thread = threading.Thread(target=calculate_bm25_scores, args=(item, sorted_list, query_word_ids, intersection))
        bm25_threads.append(thread)
        thread.start()

    # Wait for all BM25 threads to complete
    for thread in bm25_threads:
        thread.join()

    make_results(sorted_list, results)
    print(f"Displaying {len(results)} of {sum(len(data['doc_ids']) for data in inverted_data.values())} results in {t.time() - a} seconds.")
    
    return results