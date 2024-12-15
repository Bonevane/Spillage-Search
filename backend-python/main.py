from config import lexicon_file, csv_file
from index import iterate_dataset, create_inverted_index
import time as t

a = t.time()
iterate_dataset(csv_file, lexicon_file)
print(t.time() - a)

b = t.time()
create_inverted_index()
print(t.time() - b)