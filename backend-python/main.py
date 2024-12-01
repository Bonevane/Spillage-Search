from lexicon_utils import create_and_update_lexicon
from forward_index import update_forward_index

# Run the program
csv_file = "test.csv"
lexicon_file = "lexicon.csv"
forward_index_file = 'forward_index.csv'
#process_and_update_forward_index(csv_file, 'lexicon.csv', 'forward_index.csv')
create_and_update_lexicon(csv_file, lexicon_file)
update_forward_index(csv_file, lexicon_file, forward_index_file)