from lexicon_utils import create_and_update_lexicon
from forward_index import update_forward_index
from inverted_index import update_inverted_index

# Run the program
csv_file = "1000_dataset.csv"
lexicon_file = "lexicon.csv"
forward_index_file = 'forward_index.csv'
inverted_index_file = 'inverted_index.csv'

create_and_update_lexicon(csv_file, lexicon_file)
update_forward_index(csv_file, lexicon_file, forward_index_file)
update_inverted_index(forward_index_file, inverted_index_file)