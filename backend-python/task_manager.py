import asyncio
from typing import Optional, Dict, Any
from classes import UrlRequest
from medium_scraper import MediumScraper
from update_barrels import add_scraped_article_to_index
from config import processed_file, scrapped_file, lengths_file, inverted_index_folder
from nltk.corpus import stopwords
import os

# 18: Message-Passing & Networking
# TaskManager acts as a message processor.
# It consumes messages (URLs) from a queue and processes them sequentially.
# This replaces the explicit lock with a queue-based concurrency model.

class TaskManager:
    def __init__(self) -> None:
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self.status: Dict[str, Any] = {
            "is_uploading": False,
            "current_step": None,
            "progress": 0,
            "error": None,
            "success": False,
        }
        self.search_engine: Optional[Any] = None # Injected later

    def set_search_engine(self, engine: Any) -> None:
        self.search_engine = engine

    def update_status(self, **kwargs: Any) -> None:
        self.status.update(kwargs)

    async def add_task(self, url: str) -> bool:
        """
        Add a URL to the processing queue.
        Returns True if added, False if queue is full or busy (optional logic).
        """
        # For now, we allow queuing, but the status UI might only show one.
        # To mimic the previous "lock" behavior strictly:
        if self.status["is_uploading"] or not self.queue.empty():
             return False
        
        await self.queue.put(url)
        return True

    async def worker(self) -> None:
        """
        Background worker that consumes tasks from the queue.
        """
        print("Task Manager Worker Started")
        while True:
            url = await self.queue.get()
            try:
                await self._process_upload(url)
            except Exception as e:
                print(f"Worker error: {e}")
                self.update_status(error=str(e), is_uploading=False)
            finally:
                self.queue.task_done()

    async def _process_upload(self, url: str) -> None:
        if not self.search_engine:
            self.update_status(step="Error: Search Engine not initialized", error="Search Engine not initialized", success=False)
            return

        self.update_status(is_uploading=True, step="Starting upload...", progress=5, error=None, success=False)
        
        # We need to run blocking code in a thread executor to not block the async loop
        loop = asyncio.get_running_loop()
        
        try:
            # 15: Promises (awaiting the result of a threaded function)
            result = await loop.run_in_executor(None, self._sync_scrape_and_index, url)
            
            if result['success']:
                self.update_status(step="Completed", progress=100, success=True)
            else:
                self.update_status(step="Failed during scraping", error=result['message'], success=False)
                
        except Exception as e:
            self.update_status(step="Error occurred", error=str(e), success=False)
        finally:
            self.update_status(is_uploading=False)

    def _sync_scrape_and_index(self, url: str) -> Dict[str, Any]:
        """
        Synchronous wrapper for the scraping and indexing logic.
        """
        from medium_scraper import scrape_and_add_article
        
        if not self.search_engine:
            return {'success': False, 'message': 'Search Engine not initialized'}

        latest_doc_id = 0
        doc_id_file = "indexes/latest_doc_id.txt"
        if os.path.exists(doc_id_file):
            with open(doc_id_file, 'r') as f:
                latest_doc_id = int(f.read().strip())

        self.update_status(step="Extracting article content...", progress=25)
        
        result = scrape_and_add_article(
            url, 
            self.search_engine.processed_dict, 
            self.search_engine.scrapped_dict, 
            self.search_engine.lengths_dict, 
            latest_doc_id,
            processed_file, 
            scrapped_file, 
            lengths_file, 
            doc_id_file
        )

        if result['success']:
            self.update_status(step="Indexing article... This may take a few minutes", progress=70)
            stop_words = set(stopwords.words('english'))
            add_scraped_article_to_index(
                result['data'], 
                result['doc_id'], 
                self.search_engine.lexicon, 
                inverted_index_folder, 
                stop_words
            )
        
        return result
