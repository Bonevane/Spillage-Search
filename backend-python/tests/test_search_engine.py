import pytest
from unittest.mock import MagicMock, patch
from search_engine import SearchEngine
from classes import SearchResult

@pytest.fixture
def mock_search_engine():
    with patch('search_engine.load_lexicon') as mock_load_lexicon, \
         patch('search_engine.load_processed_to_dict') as mock_load_processed, \
         patch('search_engine.load_scrapped_to_dict') as mock_load_scrapped, \
         patch('search_engine.load_lengths') as mock_load_lengths, \
         patch('search_engine.preprocess_word') as mock_preprocess, \
         patch('search_engine.WordNetLemmatizer'):
        
        mock_load_lexicon.return_value = {'test': 1, 'query': 2}
        mock_load_processed.return_value = {
            1: {'title': 'Test Doc', 'url': 'http://test.com', 'tags': [], 'authors': [], 'timestamp': ''}
        }
        mock_load_scrapped.return_value = {}
        mock_load_lengths.return_value = {1: 100}
        mock_preprocess.side_effect = lambda x: x
        
        engine = SearchEngine(
            lexicon_file='lexicon.csv',
            processed_file='processed.csv',
            scrapped_file='scrapped.csv',
            lengths_file='lengths.csv',
            inverted_index_folder='indexes'
        )
        return engine

def test_search_engine_initialization(mock_search_engine):
    assert mock_search_engine.lexicon == {'test': 1, 'query': 2}
    assert mock_search_engine.processed_dict[1]['title'] == 'Test Doc'

def test_search_empty_query(mock_search_engine):
    result = mock_search_engine.search("")
    assert isinstance(result, SearchResult)
    assert result.count == 0
    assert len(result.results) == 0

@patch('search_engine.threading.Thread')
def test_search_execution(mock_thread, mock_search_engine):
    # Mock the internal methods to avoid file I/O
    # We don't mock _append_inverted_barrel_data completely, we want it to be called (or we mock it to do something)
    
    # Instead of mocking Thread to do nothing, we make it run the target immediately
    def run_target(target, args):
        target(*args)
        return MagicMock()
    
    mock_thread.side_effect = run_target

    # Mock _append_inverted_barrel_data to populate inverted_data
    def side_effect_append(word, data_dict):
        # Populate with dummy data
        data_dict[1] = {
            'doc_ids': [1],
            'frequencies': [1],
            'positions': [[1]],
            'types': [['T']]
        }
    mock_search_engine._append_inverted_barrel_data = MagicMock(side_effect=side_effect_append)
    
    # Mock _find_intersection
    mock_search_engine._find_intersection = MagicMock(return_value={1})
    
    # We can let _calculate_bm25_scores run or mock it. 
    # If we let it run, we need to make sure it works with the dummy data.
    # Let's mock it to ensure we get a result.
    def side_effect_bm25(item, results_list, query_word_ids, intersection):
        results_list.append((10.0, 1))
    mock_search_engine._calculate_bm25_scores = MagicMock(side_effect=side_effect_bm25)

    result = mock_search_engine.search("test query")
    
    assert isinstance(result, SearchResult)
    assert len(result.results) == 1
    assert result.results[0].id == 1
