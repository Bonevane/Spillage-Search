import nltk

# NLTK downloads
def download_nltk_resources() -> None:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('punkt_tab')