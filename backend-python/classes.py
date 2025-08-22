from pydantic import BaseModel
from typing import List
from typing import List, Dict, Optional, Any
from datetime import datetime
import threading
import asyncio
import aiohttp
import uuid


###
### Define the request/response body structures
###
class QueryRequest(BaseModel):
    query: str

class UrlRequest(BaseModel):
    url: str

class Result(BaseModel):
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
    results: List[Result]
    count: int
    time: float

###
### Global cache for query results
###
class QueryCache:
    def __init__(self):
        self.last_query: Optional[str] = None
        self.last_query_timestamp: Optional[datetime] = None
        self.last_results: List[Dict] = []
        self.query_id: Optional[str] = None
        self.processing_lock = threading.Lock()
        self.is_processing = False
        
    def update_cache(self, query: str, results: List[Dict]):
        """Update cache with new query and results"""
        with self.processing_lock:
            self.last_query = query
            self.last_query_timestamp = datetime.now()
            self.last_results = results[:5]  # Keep top 5 results
            self.query_id = str(uuid.uuid4())
            self.is_processing = False
            print(f"DEBUG: Cache updated - Query: '{query[:50]}...', Results: {len(results)}")
    
    def set_processing(self, query: str):
        """Mark that a query is being processed"""
        with self.processing_lock:
            self.is_processing = True
            self.last_query = query
            self.query_id = str(uuid.uuid4())
            print(f"DEBUG: Started processing query: '{query[:50]}...'")
    
    def get_cache_status(self):
        """Get current cache status"""
        with self.processing_lock:
            return {
                'has_query': self.last_query is not None,
                'query': self.last_query,
                'query_id': self.query_id,
                'results_count': len(self.last_results),
                'timestamp': self.last_query_timestamp,
                'is_processing': self.is_processing
            }

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
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
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
                            summary = data['candidates'][0]['content']['parts'][0]['text'].strip()
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
