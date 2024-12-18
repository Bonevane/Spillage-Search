# from gensim.models import KeyedVectors
# import gensim.downloader as api

# # Load pre-trained Word2Vec model (e.g., Google News vectors)
# # model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
# model = api.load("glove-wiki-gigaword-100")

# query = "apple"
# top_similar = model.most_similar(query, topn=5)
# print(top_similar)  # Output: [('sample', 0.85), ('instance', 0.83), ('illustration', 0.80)]

from lexicon_utils import load_lexicon
from config import lexicon_file
from sentence_transformers import SentenceTransformer, util
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
lexicon = load_lexicon(lexicon_file)
vocab = list(lexicon.keys())

query = "apple"
print("wow")
# vocab_embeddings = model.encode(vocab)
# np.save("embeddings.npy", vocab_embeddings)
vocab_embeddings = np.load("embeddings.npy")
print("bruh")
query_embedding = model.encode(query)


# Find top 3 similar words
similarities = util.cos_sim(query_embedding, vocab_embeddings)
top_indices = similarities.argsort(descending=True)[0][:20]
top_words = [(vocab[i], similarities[0][i].item()) for i in top_indices]
print(top_words)
