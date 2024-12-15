from lexicon_utils import create_and_update_lexicon, load_lexicon
from forward_index import update_forward_index
from inverted_index import update_inverted_barrel, load_offsets, create_offsets
from index import index_dataset, iterate_dataset
import time as t
import os

# Run the program
csv_file = "test.csv"
lexicon_file = "indices/lexicon.csv"
forward_index_folder = 'indices/forward'
inverted_index_folder = 'indices/inverted'

a = t.time()
iterate_dataset(csv_file, lexicon_file)

# index_dataset(csv_file, lexicon_file, forward_index_file)
# create_and_update_lexicon(csv_file, lexicon_file)
# update_forward_index(csv_file, lexicon_file, forward_index_file)
print(t.time() - a)
b = t.time()
barrel = 0
while True:
    if os.path.isfile(forward_index_folder + f'/forward_{barrel}.csv'):
        print(f"Creating inverted barrel {barrel}...")
        update_inverted_barrel(forward_index_folder + f'/forward_{barrel}.csv', inverted_index_folder + f'/inverted_{barrel}.csv')
        create_offsets(inverted_index_folder, barrel)
        barrel += 1
    else:
        break
    
print(t.time() - b)