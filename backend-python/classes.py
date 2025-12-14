from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, TypedDict
from datetime import datetime
import threading
import asyncio
import aiohttp
import uuid

# Shared TypedDicts for internal data flow
class ArticleData(TypedDict):
    title: str
    text: str
    url: str
    authors: List[str]
    timestamp: Optional[str]
    tags: List[str]
    thumbnail: Optional[str]
    description: str
    members_only: bool
    status_code: int

class WordDataEntry(TypedDict):
    frequency: int
    positions: List[int]
    sources: List[str]

class InvertedIndexEntry(TypedDict):
    word_id: int
    doc_ids: List[int]
    frequencies: List[int]
    positions: List[List[int]]
    sources: List[List[str]]

###
### Define the request/response body structures
###
class QueryRequest(BaseModel):
    """
    Request model for search queries.
    """
    query: str

class UrlRequest(BaseModel):
    """
    Request model for URL-based operations.
    """
    url: str

class Result(BaseModel):
    """
    Represents a single search result.
    """
    id: int
    title: str
    description: str
    thumbnail: str
    url: str
    tags: List[str]
    authors: List[str]
    date: str
    member: str

class SearchResult(BaseModel):
    """
    Represents the complete response for a search request.
    """
    results: List[Result]
    count: int
    time: float

###
### Global cache for query results
###
class QueryCache:
    """
    Thread-safe cache for storing the latest query results.
    
    Abstract Data Type for caching query state.
    Rep Invariant:
        - self._last_results contains at most 5 items.
        - if self._is_processing is True, self._last_query is not None.
    """
    def __init__(self) -> None:
        self._last_query: Optional[str] = None
        self._last_query_timestamp: Optional[datetime] = None
        self._last_results: List[Dict[str, Any]] = []
        self._query_id: Optional[str] = None
        self._processing_lock = threading.Lock()
        self._is_processing = False
        
    def update_cache(self, query: str, results: List[Dict[str, Any]]) -> None:
        """
        Update cache with new query and results.
        
        Args:
            query: The search query string.
            results: List of result dictionaries.
            
        Modifies:
            self._last_query, self._last_query_timestamp, self._last_results, self._query_id, self._is_processing
        """
        with self._processing_lock:
            self._last_query = query
            self._last_query_timestamp = datetime.now()
            self._last_results = results[:5]  # Keep top 5 results
            self._query_id = str(uuid.uuid4())
            self._is_processing = False
            print(f"DEBUG: Cache updated - Query: '{query[:50]}...', Results: {len(results)}")
    
    def set_processing(self, query: str) -> None:
        """
        Mark that a query is being processed.
        
        Args:
            query: The search query string.
        """
        with self._processing_lock:
            self._is_processing = True
            self._last_query = query
            self._query_id = str(uuid.uuid4())
            print(f"DEBUG: Started processing query: '{query[:50]}...'")
    
    def get_cache_status(self) -> Dict[str, Any]:
        """
        Get current cache status.
        
        Returns:
            A dictionary containing the cache state.
        """
        with self._processing_lock:
            return {
                'has_query': self._last_query is not None,
                'query': self._last_query,
                'query_id': self._query_id,
                'results_count': len(self._last_results),
                'timestamp': self._last_query_timestamp,
                'is_processing': self._is_processing
            }

    @property
    def last_results(self) -> List[Dict[str, Any]]:
        """
        Get the last results.
        """
        with self._processing_lock:
            return list(self._last_results) # Return a copy to preserve encapsulation

###
### New models for summarization
###
class SummarizeRequest(BaseModel):
    wait_for_results: bool = True  # Whether to wait for current query to finish
    max_wait_seconds: int = 30     # Maximum time to wait
    custom_query: Optional[str] = None  # Override cached query
    summary_length: str = "short"  # short, medium, long

class SummarizeArticleRequest(BaseModel):
    url: str
    summary_length: str = "short"  # Optional: "short", "medium", "long"

class SummarizeResponse(BaseModel):
    success: bool
    message: str
    summary: str
    query: str
    sources: List[Dict[str, Any]]
    num_sources: int
    query_id: str
    cached_at: Optional[datetime]

# Gemini RAG module
class GeminiRAGModule:
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash") -> None:
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        print(f"DEBUG: Initialized Gemini RAG with model: {model_name}")
    
    async def generate_summary(self, query: str, context: str, summary_length: str = "short") -> str:
        """Generate summary using Gemini API"""
        
        # Define prompts based on summary length
        length_prompts = {
            "short": "Provide a concise 2-3 sentence summary",
            "medium": "Provide a comprehensive summary in 4-6 sentences", 
            "long": "Provide a detailed summary in 1-2 paragraphs"
        }
        
        length_instruction = length_prompts.get(summary_length, length_prompts["short"])
        
        prompt = f"""Based on the following search results, {length_instruction} that directly answers the query: "{query}"

Search Results:
{context}

Instructions:
- Focus only on information that directly relates to the query
- Be factual and concise
- If the results don't fully answer the query, mention what information is available
- Don't include URLs or technical details unless specifically relevant
- Keep the summary under 100 words for 'short' length

Summary:"""

        try:
            url = f"{self.base_url}/{self.model_name}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,  # Lower temperature for more focused responses
                    "topK": 20,
                    "topP": 0.8,
                    "maxOutputTokens": 150 if summary_length == "short" else 300,
                    "candidateCount": 1
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'candidates' in data and len(data['candidates']) > 0:
                            summary = str(data['candidates'][0]['content']['parts'][0]['text']).strip()
                            print(f"DEBUG: Generated summary length: {len(summary)} characters")
                            return summary
                        else:
                            raise Exception("No candidates in Gemini response")
                    else:
                        error_text = await response.text()
                        raise Exception(f"Gemini API error {response.status}: {error_text}")
                        
        except Exception as e:
            print(f"DEBUG: Gemini API error: {e}")
            raise Exception(f"Failed to generate summary: {str(e)}")
