from lexicon_utils import load_lexicon
from config import lexicon_file
from sentence_transformers import SentenceTransformer, util
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
lexicon = load_lexicon(lexicon_file)
vocab = list(lexicon.keys())

query = "run"
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
