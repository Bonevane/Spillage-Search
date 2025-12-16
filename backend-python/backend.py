############################################################
# IMPORTS & ENVIRONMENT SETUP
############################################################
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import WordNetLemmatizer
from heapq import nlargest

from classes import QueryRequest, UrlRequest, SearchResult, QueryCache, SummarizeRequest, SummarizeArticleRequest, SummarizeResponse, GeminiRAGModule
from search_engine import SearchEngine
from config import inverted_index_folder, lexicon_file, processed_file, scrapped_file, received_file, lengths_file
from medium_scraper import MediumScraper
from task_manager import TaskManager

import threading
import struct
import csv
import json
import re
import asyncio
import os
import math
import time as t
from typing import List, Dict, Any, Optional

from downloads import download_nltk_resources
from dotenv import load_dotenv
load_dotenv()
download_nltk_resources()

############################################################
# FAST API SETUP
############################################################

# Global Search Engine Instance
search_engine: Optional[SearchEngine] = None
query_cache = QueryCache()
task_manager = TaskManager()

from typing import AsyncGenerator

# Use FastAPI lifespan event for startup/shutdown logic
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global search_engine
    # Startup: Initialize Search Engine
    search_engine = SearchEngine(
        lexicon_file=lexicon_file,
        processed_file=processed_file,
        scrapped_file=scrapped_file,
        lengths_file=lengths_file,
        inverted_index_folder=inverted_index_folder
    )
    
    # Inject Search Engine into Task Manager
    task_manager.set_search_engine(search_engine)
    
    # Start Task Manager Worker
    asyncio.create_task(task_manager.worker())
    
    # Startup: Initialize Gemini summarization service
    setup_gemini_summarization_service(
        api_key=os.getenv("GEMINI_API_KEY"),
        model_name="gemini-2.5-flash-lite"  # Free tier model
    )
    yield
    # Shutdown: Add any cleanup logic here if needed

app = FastAPI(lifespan=lifespan)
# upload_lock removed in favor of TaskManager queue (Message-Passing)


############################################################
# GLOBAL VARIABLES & BM25 PARAMS
############################################################

# Field size limit for CSV
csv.field_size_limit(100_000_000)


############################################################
# CORS SETUP
############################################################
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


############################################################
# SEARCH APIs
############################################################

# Search API
@app.post("/search", response_model=SearchResult)
async def search_documents(request: QueryRequest) -> SearchResult:
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search Engine not initialized")

    # Store original query and mark as processing
    original_query = request.query  # Store unprocessed query
    query_cache.set_processing(original_query)
    
    # Perform search using the SearchEngine ADT
    result = await search_engine.search(request.query)
    
    # Update cache with results
    # Convert Result objects to dictionaries for the cache if needed, 
    # or update QueryCache to accept Result objects.
    # Assuming QueryCache expects dicts based on previous code, let's convert.
    results_dicts = [r.dict() for r in result.results]
    query_cache.update_cache(original_query, results_dicts)
    
    print(f"Displaying {result.count} results in {result.time} seconds.")
   
    return result


############################################################
# UPLOAD APIS
############################################################

# Shared upload status dictionary
upload_status: Dict[str, Any] = {
    "is_uploading": False,
    "current_step": None,
    "progress": 0,
    "error": None,
    "success": False,
}

def update_status(
    step: Optional[str] = None, 
    progress: Optional[int] = None, 
    error: Optional[str] = None, 
    success: Optional[bool] = None, 
    is_uploading: Optional[bool] = None
) -> None:
    if step is not None:
        upload_status["current_step"] = step
    if progress is not None:
        upload_status["progress"] = progress
    if error is not None:
        upload_status["error"] = error
    if success is not None:
        upload_status["success"] = success
    if is_uploading is not None:
        upload_status["is_uploading"] = is_uploading


def threaded_upload(url: str) -> None:
    if search_engine is None:
        update_status(step="Error: Search Engine not initialized", error="Search Engine not initialized", success=False)
        return

    try:
        update_status(is_uploading=True, step="Starting upload...", progress=5, error=None, success=False)

        from medium_scraper import scrape_and_add_article
        from update_barrels import add_scraped_article_to_index

        latest_doc_id = 0
        doc_id_file = "indexes/latest_doc_id.txt"
        if os.path.exists(doc_id_file):
            with open(doc_id_file, 'r') as f:
                latest_doc_id = int(f.read().strip())

        update_status(step="Extracting article content...", progress=25)
        
        # Use data structures from search_engine
        result = scrape_and_add_article(
            url, 
            search_engine.processed_dict, 
            search_engine.scrapped_dict, 
            search_engine.lengths_dict, 
            latest_doc_id,
            processed_file, 
            scrapped_file, 
            lengths_file, 
            doc_id_file
        )

        if result['success']:
            update_status(step="Indexing article... This may take a few minutes", progress=70)
            stop_words = set(stopwords.words('english'))
            add_scraped_article_to_index(
                result['data'], 
                result['doc_id'], 
                search_engine.lexicon, 
                inverted_index_folder, 
                stop_words
            )
            update_status(step="Completed", progress=100, success=True)
        else:
            update_status(step="Failed during scraping", error=result['message'], success=False)

    except Exception as e:
        update_status(step="Error occurred", error=str(e), success=False)

    finally:
        update_status(is_uploading=False)


@app.post("/upload-url")
async def upload_url(request: UrlRequest) -> JSONResponse:
    url = request.url

    # 18: Message-Passing
    # Send message (URL) to the TaskManager queue
    success = await task_manager.add_task(url)
    
    if not success:
        raise HTTPException(status_code=400, detail="A process is already running. Please try again later.")

    # Reset status for new upload (handled by TaskManager, but we can set initial state here if needed)
    task_manager.update_status(is_uploading=True, step="Queued for upload...", progress=0, error=None, success=False)

    return JSONResponse(content={"message": "Upload queued. You can continue searching."})


@app.get("/upload-status")
async def upload_status_endpoint() -> JSONResponse:
    return JSONResponse(content=task_manager.status)



############################################################
# SUMMARY APIS + RAG MODULE
############################################################

# Global RAG module instance
gemini_rag: Optional[GeminiRAGModule] = None

def initialize_gemini_rag(api_key: str, model_name: str = "gemini-2.5-flash-lite") -> None:
    """Initialize the Gemini RAG module - call this at startup"""
    global gemini_rag
    gemini_rag = GeminiRAGModule(api_key, model_name)
    print("DEBUG: Gemini RAG module initialized")

def convert_search_results_to_rag_format(search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
async def summarize_results(request: SummarizeRequest) -> SummarizeResponse:
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
    
    query = request.custom_query or str(cache_status['query'])
    cached_results = query_cache.last_results
    
    if not cached_results:
        return SummarizeResponse(
            success=False,
            message="No search results available for summarization",
            summary="No relevant results were found for your query.",
            query=query,
            sources=[],
            num_sources=0,
            query_id=str(cache_status['query_id']),
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
            query_id=str(cache_status['query_id']),
            cached_at=cache_status['timestamp']
        )
        
    except Exception as e:
        print(f"DEBUG: Error during summarization: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )


@app.post("/summarize-article")
async def summarize_article(request: SummarizeArticleRequest) -> Dict[str, Any]:
    if gemini_rag is None:
        raise HTTPException(status_code=503, detail="Gemini RAG module not initialized")

    # Scrape the article
    scraper = MediumScraper()
    article_data = scraper.scrape_article(request.url)
    
    if not article_data or not article_data.get("title"):
        raise HTTPException(status_code=400, detail="Failed to scrape article or no title found")
    
    # Prepare context for Gemini
    context = f"Title: {article_data['title']}\n\n{article_data['text']}\n\nDescription: {article_data.get('description', '')}"
    query = f"Summarize the following Medium article: {article_data['title']}"
    
    # Generate summary using Gemini
    try:
        summary = await gemini_rag.generate_summary(query, context, request.summary_length)
        return {
            "success": True,
            "summary": summary,
            "title": article_data['title'],
            "url": request.url,
            "authors": article_data.get('authors', []),
            "tags": article_data.get('tags', []),
            "thumbnail": article_data.get('thumbnail', None),
            "description": article_data.get('description', ""),
            "members_only": article_data.get('members_only', False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

async def generate_summary_with_gemini(query: str, search_results: List[Dict[str, Any]], summary_length: str = "short") -> Dict[str, Any]:
    """Generate summary using Gemini with pre-formatted results"""
    print(f"DEBUG: Generating Gemini summary for: '{query[:50]}...'")
    
    if gemini_rag is None:
        return {
            'success': False,
            'message': 'Gemini RAG module not initialized',
            'summary': 'Service unavailable',
            'sources': [],
            'num_sources': 0
        }

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
def get_search_status() -> Dict[str, Any]:
    """Get current search cache status"""
    cache_status = query_cache.get_cache_status()
    return {
        "cache_status": cache_status,
        "gemini_rag_initialized": gemini_rag is not None
    }

# Optional: Clear cache endpoint
@app.post("/search/clear-cache")
def clear_search_cache() -> Dict[str, str]:
    """Clear the search cache"""
    global query_cache
    query_cache = QueryCache()
    return {"message": "Search cache cleared successfully"}

# Setup function for Gemini
def setup_gemini_summarization_service(api_key: Optional[str], model_name: str = "gemini-2.5-flash-lite") -> bool:
    """Setup the Gemini summarization service - call this at app startup"""
    if not api_key:
        print("DEBUG: No API key provided for Gemini summarization service")
        return False
        
    try:
        initialize_gemini_rag(api_key, model_name)
        print("DEBUG: Gemini summarization service setup completed")
        return True
    except Exception as e:
        print(f"DEBUG: Failed to setup Gemini summarization service: {e}")
        return False