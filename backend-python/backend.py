from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import WordNetLemmatizer
from heapq import nlargest

from classes import QueryRequest, UrlRequest, SearchResult, Result, QueryCache, SummarizeRequest, SummarizeResponse, GeminiRAGModule
from lexicon_utils import load_lexicon, preprocess_word
from config import inverted_index_folder, lexicon_file, processed_file, scrapped_file, received_file, lengths_file
from csv_utils import load_processed_to_dict, load_scrapped_to_dict, load_lengths

import threading
import struct
import csv
import json
import re
import asyncio
import os
import math
import time as t
from typing import List, Dict, Optional, Any

from downloads import download_nltk_resources
from dotenv import load_dotenv
load_dotenv()

# download_nltk_resources()
app = FastAPI()
upload_lock = threading.Lock()

@app.on_event("startup")
async def startup_event():
    # Initialize the Gemini summarization service
    setup_gemini_summarization_service(
        api_key=os.getenv("GEMINI_API_KEY"),
        model_name="gemini-1.5-flash"  # Free tier model
    )

# Loading lexicon, processed data, scrapped data and lengths data
lexicon = load_lexicon(lexicon_file)
vocab = list(lexicon.keys())
processed_dict = load_processed_to_dict(processed_file)
scrapped_dict = load_scrapped_to_dict(scrapped_file)
lengths_dict = load_lengths(lengths_file)

k = 1.5
b = 0.75
N = len(processed_dict)
WORD_IN_QUERY_VAR = 3
INTERSECTION_VAR = 10
TITLE_CONTAINS_QUERY_VAR = 100
TITLE_VAR = 12
AUTHOR_VAR = 6
TAG_VAR = 8
avgdl = sum(lengths_dict.values()) / N

# Loading lemmatizer and intializing it (For some reason it takes too long to lemmatize the first time)
lemmatizer = WordNetLemmatizer()
preprocess_word('apple')

# Field size limit for CSV
csv.field_size_limit(100_000_000)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





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


def calculate_bm25_scores(item, results_list, query_word_ids, intersection):
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
            score *= INTERSECTION_VAR
        
        if word_id in query_word_ids:
            score *= WORD_IN_QUERY_VAR
        
        if "T" in source: 
            score *= TITLE_VAR
        if "A" in source:
            score *= AUTHOR_VAR
        if "Ta" in source:
            score *= TAG_VAR
        
        results_list.append((score, doc_id))

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
    for score, doc_ids in sorted_list: #[::-1]:
        if doc_ids in processed_doc_ids:
            continue  # Skip duplicate entries
        processed_doc_ids.add(doc_ids)
        
        processed_data = processed_dict[doc_ids]
        
        description = "No description available"
        thumbnail = "No thumbnail available"
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
            "authors": processed_data['authors'],
            "date": processed_data['timestamp'],
            "member" : member
        })
        
        counter += 1
        if counter >= 100:
            break

def get_top_100_results(score_docid_list):
    return nlargest(150, score_docid_list, key=lambda x: x[0])



# Global cache instance
query_cache = QueryCache()

# Your existing search function with caching added
@app.post("/search", response_model=SearchResult)
def search_documents(request: QueryRequest):
    a = t.time()
    
    # Store original query and mark as processing
    original_query = request.query  # Store unprocessed query
    query_cache.set_processing(original_query)
    
    # Your existing search logic (unchanged)
    query = request.query.lower()
    results = []
    bm25_scores = []
    inverted_data = {}
    results_list = []
    query = word_tokenize(query)
    query = list(set(query))
    query = query[:10]
    query = [preprocess_word(word) for word in query if preprocess_word(word) in lexicon]  # Preprocess each word in the query
    query_word_ids = [lexicon[word] for word in query if word in lexicon]
   
    if not query:
        # Even for empty results, update cache
        query_cache.update_cache(original_query, [])
        return {"results": [], "count": 0, "time": t.time() - a}
   
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
        thread = threading.Thread(target=calculate_bm25_scores, args=(item, results_list, query_word_ids, intersection))
        bm25_threads.append(thread)
        thread.start()
    # Wait for all BM25 threads to complete
    for thread in bm25_threads:
        thread.join()
    sorted_list = get_top_100_results(results_list)
    make_results(sorted_list, results)
    total_results = sum(len(data['doc_ids']) for data in inverted_data.values())
    
    # Update cache with results
    query_cache.update_cache(original_query, results)
    
    print(f"Displaying {len(results)} of {sum(len(data['doc_ids']) for data in inverted_data.values())} results in {t.time() - a} seconds.")
   
    return {"results": results, "count": total_results, "time": t.time() - a}


# UPLOAD APIs
def threaded_upload(url):
    try:
        from medium_scraper import scrape_and_add_article
        from update_barrels import add_scraped_article_to_index

        latest_doc_id = 0
        doc_id_file = "indexes/latest_doc_id.txt"
        if os.path.exists(doc_id_file):
            with open(doc_id_file, 'r') as f:
                latest_doc_id = int(f.read().strip())

        result = scrape_and_add_article(
            url, processed_dict, scrapped_dict, lengths_dict, latest_doc_id,
            processed_file, scrapped_file, lengths_file, doc_id_file
        )

        if result['success']:
            stop_words = set(stopwords.words('english'))
            add_scraped_article_to_index(
                result['data'], result['doc_id'], lexicon, inverted_index_folder, stop_words
            )
            print("Article uploaded and indexed successfully!")
        else:
            print(f"Error: {result['message']}")
    except Exception as e:
        print(f"Error processing article: {str(e)}")
    finally:
        upload_lock.release()

@app.post("/upload-url")
async def upload_url(request: UrlRequest):
    url = request.url

    # Try to acquire the lock for upload
    if not upload_lock.acquire(blocking=False):
        raise HTTPException(status_code=400, detail="A process is already running. Please try again later.")

    # Start the upload in a separate thread
    thread = threading.Thread(target=threaded_upload, args=(url,))
    thread.start()
    return JSONResponse(content={"message": "Upload started in background. You can continue searching."})










# Global RAG module instance
gemini_rag = None

def initialize_gemini_rag(api_key: str, model_name: str = "gemini-1.5-flash"):
    """Initialize the Gemini RAG module - call this at startup"""
    global gemini_rag
    gemini_rag = GeminiRAGModule(api_key, model_name)
    print("DEBUG: Gemini RAG module initialized")

def convert_search_results_to_rag_format(search_results: List[Dict]) -> List[Dict]:
    """Convert your search results format to RAG module format"""
    print(f"DEBUG: Converting {len(search_results)} search results to RAG format")
    
    converted_results = []
    for i, result in enumerate(search_results):
        try:
            # Adapt this based on your actual search result structure
            converted_result = {
                'doc_id': result.get('id', i),  # Adjust field name as needed
                'title': result.get('title', ''),
                'url': result.get('url', ''),
                'description': result.get('description', result.get('snippet', '')),
                'relevance_score': result.get('score', 0.0),
                'full_content': None  # Will be populated by RAG module if needed
            }
            converted_results.append(converted_result)
            print(f"DEBUG: Converted result {i+1}: '{converted_result['title'][:50]}...'")
        except Exception as e:
            print(f"DEBUG: Error converting result {i}: {e}")
            continue
    
    return converted_results

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_results(request: SummarizeRequest):
    """Generate summary based on cached search results using Gemini"""
    print(f"DEBUG: Summarize request received - wait_for_results: {request.wait_for_results}")
    
    # Check if Gemini RAG module is initialized
    if gemini_rag is None:
        raise HTTPException(
            status_code=500, 
            detail="Gemini RAG module not initialized. Please configure the summarization service."
        )
    
    # Wait for current query to finish processing if requested
    if request.wait_for_results:
        wait_count = 0
        max_wait = request.max_wait_seconds
        
        print(f"DEBUG: Waiting for query processing to complete (max {max_wait}s)")
        
        while wait_count < max_wait:
            cache_status = query_cache.get_cache_status()
            
            if not cache_status['is_processing']:
                print(f"DEBUG: Query processing completed after {wait_count}s")
                break
                
            await asyncio.sleep(1)
            wait_count += 1
        
        if wait_count >= max_wait:
            print(f"DEBUG: Timeout waiting for query processing")
            raise HTTPException(
                status_code=408,
                detail=f"Timeout waiting for search results (waited {max_wait}s)"
            )
    
    # Get cached results
    cache_status = query_cache.get_cache_status()
    
    if not cache_status['has_query']:
        raise HTTPException(
            status_code=404,
            detail="No cached query found. Please perform a search first."
        )
    
    query = request.custom_query or cache_status['query']
    cached_results = query_cache.last_results
    
    if not cached_results:
        return SummarizeResponse(
            success=False,
            message="No search results available for summarization",
            summary="No relevant results were found for your query.",
            query=query,
            sources=[],
            num_sources=0,
            query_id=cache_status['query_id'],
            cached_at=cache_status['timestamp']
        )
    
    print(f"DEBUG: Starting summarization for query: '{query[:50]}...'")
    print(f"DEBUG: Using {len(cached_results)} cached results")
    
    try:
        # Convert search results to RAG format
        rag_results = convert_search_results_to_rag_format(cached_results[:3])  # Use top 3
        
        if not rag_results:
            raise HTTPException(
                status_code=500,
                detail="Could not process search results for summarization"
            )
        
        # Generate summary using Gemini
        summary_result = await generate_summary_with_gemini(query, rag_results, request.summary_length)
        
        return SummarizeResponse(
            success=summary_result['success'],
            message=summary_result['message'],
            summary=summary_result['summary'],
            query=query,
            sources=summary_result['sources'],
            num_sources=summary_result['num_sources'],
            query_id=cache_status['query_id'],
            cached_at=cache_status['timestamp']
        )
        
    except Exception as e:
        print(f"DEBUG: Error during summarization: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )

async def generate_summary_with_gemini(query: str, search_results: List[Dict], summary_length: str = "short") -> Dict[str, Any]:
    """Generate summary using Gemini with pre-formatted results"""
    print(f"DEBUG: Generating Gemini summary for: '{query[:50]}...'")
    
    try:
        # Prepare context from search results (keep it concise for short summaries)
        context_parts = []
        max_content_length = 800 if summary_length == "short" else 1500
        
        for i, result in enumerate(search_results, 1):
            content = result.get('description', '') or result.get('full_content', '')
            # Truncate content to keep context manageable
            content = content[:max_content_length] if content else ""
            
            context_part = f"""Source {i}: {result['title']}
{content}"""
            context_parts.append(context_part)
        
        context = "\n\n".join(context_parts)
        print(f"DEBUG: Prepared context length: {len(context)} characters")
        
        # Generate summary using Gemini
        summary = await gemini_rag.generate_summary(query, context, summary_length)
        
        # Prepare sources
        sources = [
            {
                'title': result['title'],
                'url': result['url'],
                'doc_id': result['doc_id'],
                'relevance_score': result.get('relevance_score', 0.0)
            }
            for result in search_results
        ]
        
        return {
            'success': True,
            'message': f'Summary generated successfully using Gemini ({summary_length} format)',
            'summary': summary,
            'sources': sources,
            'num_sources': len(sources)
        }
        
    except Exception as e:
        print(f"DEBUG: Gemini summary generation failed: {e}")
        return {
            'success': False,
            'message': f'Error generating summary: {str(e)}',
            'summary': 'An error occurred while processing your query. Please try again.',
            'sources': [],
            'num_sources': 0
        }

# Optional: Endpoint to check cache status
@app.get("/search/status")
def get_search_status():
    """Get current search cache status"""
    cache_status = query_cache.get_cache_status()
    return {
        "cache_status": cache_status,
        "gemini_rag_initialized": gemini_rag is not None
    }

# Optional: Clear cache endpoint
@app.post("/search/clear-cache")
def clear_search_cache():
    """Clear the search cache"""
    global query_cache
    query_cache = QueryCache()
    return {"message": "Search cache cleared successfully"}

# Setup function for Gemini
def setup_gemini_summarization_service(api_key: str, model_name: str = "gemini-1.5-flash"):
    """Setup the Gemini summarization service - call this at app startup"""
    try:
        initialize_gemini_rag(api_key, model_name)
        print("DEBUG: Gemini summarization service setup completed")
        return True
    except Exception as e:
        print(f"DEBUG: Failed to setup Gemini summarization service: {e}")
        return False