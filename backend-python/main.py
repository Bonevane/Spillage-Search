from lexicon_utils import create_and_update_lexicon
from forward_index import update_forward_index
from inverted_index import update_inverted_index
from index import index_dataset, iterate_dataset
import time as t

# Run the program
csv_file = "1000_dataset.csv"
lexicon_file = "indices/lexicon.csv"
forward_index_file = 'indices/forward_index.csv'
inverted_index_file = 'indices/inverted_index.csv'

a = t.time()
iterate_dataset(csv_file, lexicon_file)

# index_dataset(csv_file, lexicon_file, forward_index_file)
# create_and_update_lexicon(csv_file, lexicon_file)
# update_forward_index(csv_file, lexicon_file, forward_index_file)
print(t.time() - a)
b = t.time()
update_inverted_index(forward_index_file, inverted_index_file)
print(t.time() - b)