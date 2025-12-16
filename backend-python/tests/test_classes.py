import pytest
from classes import QueryCache
import threading
import time

def test_query_cache_initialization():
    cache = QueryCache()
    status = cache.get_cache_status()
    assert status['has_query'] is False
    assert status['query'] is None
    assert status['results_count'] == 0
    assert status['is_processing'] is False

def test_query_cache_update():
    cache = QueryCache()
    query = "test query"
    results = [{"id": 1, "title": "Test"}, {"id": 2, "title": "Test 2"}]
    
    cache.update_cache(query, results)
    
    status = cache.get_cache_status()
    assert status['has_query'] is True
    assert status['query'] == query
    assert status['results_count'] == 2
    assert status['is_processing'] is False

def test_query_cache_limit():
    cache = QueryCache()
    query = "test query"
    # Create 10 results
    results = [{"id": i, "title": f"Test {i}"} for i in range(10)]
    
    cache.update_cache(query, results)
    
    status = cache.get_cache_status()
    assert status['results_count'] == 5  # Should be limited to 5

def test_query_cache_processing():
    cache = QueryCache()
    query = "processing query"
    
    cache.set_processing(query)
    
    status = cache.get_cache_status()
    assert status['is_processing'] is True
    assert status['query'] == query

def test_query_cache_thread_safety():
    """Test that cache handles concurrent updates correctly"""
    cache = QueryCache()
    
    def update_worker(i):
        results = [{"id": i, "title": f"Thread {i}"}]
        cache.update_cache(f"query {i}", results)
        
    threads = []
    for i in range(10):
        t = threading.Thread(target=update_worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    status = cache.get_cache_status()
    assert status['has_query'] is True
    assert status['results_count'] == 1
