from lexicon_utils import load_lexicon
from config import lexicon_file
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
lexicon = load_lexicon(lexicon_file)
vocab = list(lexicon.keys())
print("Model and vocab loaded!")

vocab_embeddings = model.encode(vocab)
np.save("embeddings.npy", vocab_embeddings)
vocab_embeddings = np.load("embeddings.npy")
print("Embeddings saved and loaded!")