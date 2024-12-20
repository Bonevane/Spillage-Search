from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from concurrent.futures import ProcessPoolExecutor
from nltk.tokenize import word_tokenize
from nltk import WordNetLemmatizer
from sentence_transformers import SentenceTransformer, util
import numpy as np
from pydantic import BaseModel
from typing import List

from lexicon_utils import load_lexicon, preprocess_word
from inverted_index import load_offsets
from index import iterate_dataset, create_inverted_index
from config import inverted_index_folder, lexicon_file, processed_file, scrapped_file, received_file, lengths_file
from csv_utils import load_processed_to_dict, load_scrapped_to_dict, load_lengths

import struct
import csv
import json
import re
import io
import os
import math

k = 1.5
b = 0.75
N = 192000
avgdl = 500

app = FastAPI()

# Loading transformer model and vocab embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
vocab_embeddings = np.load("embeddings.npy")
print("Model and embeddings loaded successfully.")

# Loading lexicon, processed data, scrapped data and lengths data
lexicon = load_lexicon(lexicon_file)
vocab = list(lexicon.keys())
processed_dict = load_processed_to_dict(processed_file)
scrapped_dict = load_scrapped_to_dict(scrapped_file)
lengths_dict = load_lengths(lengths_file)

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



@app.post("/search", response_model=List[SearchResult])
def search_documents(request: QueryRequest):
    query = request.query.lower()

    results = []
    bm25_scores = []
    all_top_words = []

    query = word_tokenize(query)
    query = [preprocess_word(word) for word in query if preprocess_word(word) in lexicon]  # Preprocess each word in the query
    
    # Encode all query words at once
    query_embeddings = model.encode(query)  # 'query' is a list of preprocessed words
    # Compute similarities between query embeddings and all vocabulary embeddings
    similarities = util.cos_sim(query_embeddings, vocab_embeddings)  # Shape: (len(query), len(vocab))
    # Iterate over each query word and its similarity vector
    for idx, q_word in enumerate(query):
        similarity_row = similarities[idx]
        # Get the indices of the top 5 similar words (excluding the query word itself)
        top_indices = similarity_row.argsort(descending=True)[1:5]
        # Retrieve the top words and their similarity scores
        top_words = [(vocab[i], similarity_row[i].item()) for i in top_indices]
        all_top_words.append((q_word, top_words))
    # 'all_top_words' now contains the top similar words for each word in 'query'
    print(all_top_words)
    
    
    
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
            IDF = math.log10((N - len(doc_frequency_pairs) + 0.5) / (len(doc_frequency_pairs) + 0.5))
            
            
            for doc_ids, frequencies in doc_frequency_pairs:
                processed_data = processed_dict[doc_ids]
                
                length = lengths_dict[doc_ids]
                TF = frequencies / (frequencies + k * (1 - b + b * length / avgdl))
                score = TF * IDF
                bm25_scores.append((doc_ids, score))
            
            bm25_scores = sorted(bm25_scores, key=lambda x: x[1], reverse=True)
            top_n_documents = bm25_scores[:20]
            print(bm25_scores[:20])
            
            for doc_ids, frequencies in top_n_documents:
                processed_data = processed_dict[doc_ids]
                
                description = "Placeholder description"
                thumbnail = "Placeholder thumbnail"
                member = "No"
                
                try:
                    description = scrapped_dict[int(doc_ids)]['description']
                    thumbnail = scrapped_dict[int(doc_ids)]['url']
                    member = scrapped_dict[int(doc_ids)]['member only']
                    print(scrapped_dict[int(doc_ids)]['member only'])
                except (Exception):
                    print(f'Description not found for {doc_ids}')
                
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
            
        except (KeyError):
            print(f'Word {word} not in Lexicon')

    
    return results