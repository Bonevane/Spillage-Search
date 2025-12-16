import requests
import json
import time

# Base URL (adjust to your FastAPI server)
BASE_URL = "https://spillage-search-ancient-frog-4456.fly.dev"  # Change this to your server URL

def test_search_endpoint():
    """Test the search endpoint"""
    print("=== Testing Search Endpoint ===")
    
    search_data = {
        "query": "how to fix mental health",
    }
    
    try:
        response = requests.post(f"{BASE_URL}/search", json=search_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_summarization_endpoint():
    """Test the summarization endpoint"""
    print("\n=== Testing Summarization Endpoint ===")
    
    # Test with different summary lengths
    for length in ["short", "medium", "long"]:
        print(f"\n--- Testing {length} summary ---")
        
        summarize_data = {
            "wait_for_results": True,
            "max_wait_seconds": 30,
            "summary_length": length
        }
        
        try:
            response = requests.post(f"{BASE_URL}/summarize", json=summarize_data)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success: {result['success']}")
                print(f"Query: {result['query']}")
                print(f"Summary: {result['summary']}")
                print(f"Sources: {result['num_sources']}")
            else:
                print(f"Error Response: {response.text}")
                
        except Exception as e:
            print(f"Error: {e}")

def test_status_endpoint():
    """Test the status endpoint"""
    print("\n=== Testing Status Endpoint ===")
    
    try:
        response = requests.get(f"{BASE_URL}/search/status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_clear_cache_endpoint():
    """Test the clear cache endpoint"""
    print("\n=== Testing Clear Cache Endpoint ===")
    
    try:
        response = requests.post(f"{BASE_URL}/search/clear-cache")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def run_full_test_sequence():
    """Run a complete test sequence"""
    print("Starting Full Test Sequence...")
    
    # 1. Check initial status
    test_status_endpoint()
    
    # 2. Perform a search
    search_result = test_search_endpoint()
    
    # 3. Wait a moment for processing
    print("\nWaiting 2 seconds for search processing...")
    time.sleep(2)
    
    # 4. Check status after search
    test_status_endpoint()
    
    # 5. Test summarization
    if search_result and search_result.get('count', 0) > 0:
        test_summarization_endpoint()
    else:
        print("Skipping summarization test - no search results")
    
    # 6. Clear cache
    test_clear_cache_endpoint()
    
    print("\nTest sequence completed!")

if __name__ == "__main__":
    run_full_test_sequence()