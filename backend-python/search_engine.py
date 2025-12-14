import math
import time as t
import asyncio
from typing import List, Dict, Any, Tuple, Set, Optional
from heapq import nlargest
from nltk.tokenize import word_tokenize
from nltk import WordNetLemmatizer

from classes import SearchResult, Result
from lexicon_utils import load_lexicon, preprocess_word
from csv_utils import load_processed_to_dict, load_scrapped_to_dict, load_lengths
from index_reader import IndexReader, FileIndexReader
from query_parser import QueryParser, QueryNode, Term, And, Or, Not

# 08: Interfaces & Subtyping
# SearchEngine implements the search logic using injected dependencies.

class SearchEngine:
    """
    A search engine implementation using BM25 ranking and inverted indices.
    """
    
    def __init__(
        self,
        lexicon_file: str,
        processed_file: str,
        scrapped_file: str,
        lengths_file: str,
        inverted_index_folder: str,
        index_reader: Optional[IndexReader] = None
    ) -> None:
        print("Loading Search Engine Data...")
        self.lexicon: Dict[str, int] = load_lexicon(lexicon_file)
        self.processed_dict: Dict[int, Dict[str, Any]] = load_processed_to_dict(processed_file)
        self.scrapped_dict: Dict[int, Dict[str, Any]] = load_scrapped_to_dict(scrapped_file)
        self.lengths_dict: Dict[int, int] = load_lengths(lengths_file)
        
        # Dependency Injection
        if index_reader:
            self.index_reader = index_reader
        else:
            self.index_reader = FileIndexReader(inverted_index_folder)
        
        self.N = len(self.processed_dict)
        self.avgdl = sum(self.lengths_dict.values()) / self.N if self.N > 0 else 0
        
        # BM25 Parameters
        self.k = 1.5
        self.b = 0.75
        self.WORD_IN_QUERY_VAR = 3
        self.INTERSECTION_VAR = 10
        self.TITLE_CONTAINS_QUERY_VAR = 100
        self.TITLE_VAR = 12
        self.AUTHOR_VAR = 6
        self.TAG_VAR = 8
        
        self.lemmatizer = WordNetLemmatizer()
        preprocess_word('apple') # Pre-warm
        print("Search Engine Initialized.")

    # 14: Concurrency (Async)
    async def _fetch_data_for_query(self, query_node: QueryNode, data_cache: Dict[str, Any]) -> None:
        """
        Recursively fetch data for all terms in the query.
        """
        if isinstance(query_node, Term):
            word = query_node.word
            if word not in data_cache:
                processed_word = preprocess_word(word)
                if processed_word in self.lexicon:
                    word_id = self.lexicon[processed_word]
                    data = await self.index_reader.get_word_data(processed_word, word_id)
                    if data:
                        data_cache[word] = data
        elif isinstance(query_node, (And, Or)):
            await asyncio.gather(
                self._fetch_data_for_query(query_node.left, data_cache),
                self._fetch_data_for_query(query_node.right, data_cache)
            )
        elif isinstance(query_node, Not):
            await self._fetch_data_for_query(query_node.operand, data_cache)

    def _evaluate_boolean(self, query_node: QueryNode, data_cache: Dict[str, Any]) -> Set[int]:
        """
        Evaluate the boolean query to get a set of matching document IDs.
        """
        if isinstance(query_node, Term):
            data = data_cache.get(query_node.word)
            if data:
                return set(data['doc_ids'])
            return set()
        elif isinstance(query_node, And):
            left_set = self._evaluate_boolean(query_node.left, data_cache)
            right_set = self._evaluate_boolean(query_node.right, data_cache)
            return left_set & right_set
        elif isinstance(query_node, Or):
            left_set = self._evaluate_boolean(query_node.left, data_cache)
            right_set = self._evaluate_boolean(query_node.right, data_cache)
            return left_set | right_set
        elif isinstance(query_node, Not):
            # NOT is tricky in search. Usually implies "AND NOT".
            # Here we return the universe minus the set, but practically we intersect later.
            # For simplicity, let's assume NOT is only used in conjunction or we return empty (unsafe).
            # Better: Return all docs minus this set.
            operand_set = self._evaluate_boolean(query_node.operand, data_cache)
            all_docs = set(self.processed_dict.keys())
            return all_docs - operand_set
        return set()

    def _calculate_bm25_score(
        self, 
        doc_id: int, 
        query_terms: List[str], 
        data_cache: Dict[str, Any],
        boolean_hits: Set[int]
    ) -> float:
        """
        Calculate BM25 score for a single document.
        """
        score = 0.0
        length = self.lengths_dict.get(doc_id, 0)
        if length == 0:
            return 0.0
            
        for term in query_terms:
            data = data_cache.get(term)
            if not data:
                continue
                
            doc_ids = data['doc_ids']
            if doc_id not in doc_ids:
                continue
                
            idx = doc_ids.index(doc_id)
            frequency = data['frequencies'][idx]
            sources = data['types'][idx]
            
            # IDF
            n = len(doc_ids)
            IDF = math.log10((self.N - n + 0.5) / (n + 0.5))
            
            TF = frequency / (frequency + self.k * (1 - self.b + self.b * length / self.avgdl))
            term_score = TF * IDF * 100
            
            if "T" in sources: term_score *= self.TITLE_VAR
            if "A" in sources: term_score *= self.AUTHOR_VAR
            if "Ta" in sources: term_score *= self.TAG_VAR
            
            score += term_score
            
        if doc_id in boolean_hits:
            score *= self.INTERSECTION_VAR
            
        return score

    async def search(self, query_str: str) -> SearchResult:
        """
        Perform a search query using async I/O and boolean parsing.
        """
        start_time = t.time()
        
        # 1. Parse Query
        parser = QueryParser(query_str)
        query_ast = parser.parse()
        
        # 2. Fetch Data (Async)
        data_cache: Dict[str, Any] = {}
        await self._fetch_data_for_query(query_ast, data_cache)
        
        # 3. Boolean Evaluation (Filtering)
        # If the query is just terms (implicit AND/OR), we might want to rank all documents 
        # that contain ANY term, but boost those that satisfy the boolean logic.
        # For strict boolean search, we only return hits.
        # Let's do a hybrid: Rank all docs that appear in data_cache, but boost boolean hits.
        
        boolean_hits = self._evaluate_boolean(query_ast, data_cache)
        
        # Collect all candidate documents (Union of all terms)
        candidate_docs: Set[int] = set()
        for data in data_cache.values():
            candidate_docs.update(data['doc_ids'])
            
        # If strict boolean is desired, uncomment:
        # candidate_docs = boolean_hits 
        
        if not candidate_docs:
             return SearchResult(results=[], count=0, time=t.time() - start_time)

        # 4. Scoring (BM25)
        # Extract simple terms for BM25
        # We can walk the AST or just use the keys in data_cache
        query_terms = list(data_cache.keys())
        
        results_list: List[Tuple[float, int]] = []
        
        # This loop is CPU bound. In a real heavy app, we might offload to a ProcessPool.
        for doc_id in candidate_docs:
            score = self._calculate_bm25_score(doc_id, query_terms, data_cache, boolean_hits)
            results_list.append((score, doc_id))
            
        # 5. Sort and Format
        sorted_list = nlargest(150, results_list, key=lambda x: x[0])
        final_results = self._make_results(sorted_list)
        
        return SearchResult(
            results=final_results,
            count=len(candidate_docs),
            time=t.time() - start_time
        )

    def _make_results(self, sorted_list: List[Tuple[float, int]]) -> List[Result]:
        results: List[Result] = []
        processed_doc_ids: Set[int] = set()
        
        for score, doc_id in sorted_list:
            if doc_id in processed_doc_ids:
                continue
            processed_doc_ids.add(doc_id)
            
            if doc_id not in self.processed_dict:
                continue
                
            processed_data = self.processed_dict[doc_id]
            
            description = "No description available"
            thumbnail = "No thumbnail available"
            member = "No"
            
            if doc_id in self.scrapped_dict:
                scrapped_data = self.scrapped_dict[doc_id]
                description = scrapped_data.get('description', description)
                thumbnail = scrapped_data.get('url', thumbnail)
                member = scrapped_data.get('member only', member)
            
            results.append(Result(
                id=doc_id,
                title=processed_data.get('title', 'No Title'),
                description=description,
                thumbnail=thumbnail,
                url=processed_data.get('url', ''),
                tags=processed_data.get('tags', []),
                authors=processed_data.get('authors', []),
                date=processed_data.get('timestamp', ''),
                member=member
            ))
                
        return results
