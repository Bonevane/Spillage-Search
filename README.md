# Spillage Search

<div align="center">

![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Next JS](https://img.shields.io/badge/Next-black?style=flat&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=flat&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-886FBF?style=flat&logo=googlegemini&logoColor=fff)
![NLTK](https://img.shields.io/badge/NLTK-green?style=flat)

</div>

A high-performance search engine for Medium articles built on Google's foundational search architecture research. Features AI-powered summaries, real-time indexing, and lightning-fast BM25 search scoring across 190k+ articles.

## 🚀 Features

- **Advanced Search**: BM25 scoring algorithm with multi-field search (title, content, tags, authors)
- **AI Summaries**: Google Gemini-powered article summarization
- **Real-time Indexing**: Add new Medium articles instantly
- **Smart Filtering**: Sort by relevancy, date, and more
- **Rich Results**: Thumbnails, descriptions, author info, and tags
- **Live Status Updates**: Real-time article uploads
- **Intelligent Caching**: Query caching for improved performance
- **Members Only Content**: View member's only content for free on Freedium

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### 1. Backend Setup

Navigate to the backend directory and install dependencies:

```bash
cd backend-python
pip install -r requirements.txt
```

Set up environment variables:

```bash
cp .env.example .env
# Add your Google Gemini API key to .env
GEMINI_API_KEY=your_api_key_here
```

Download required NLTK resources:

```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
```

### 2. Frontend Setup

Navigate to the frontend directory and install dependencies:

```bash
cd frontend-next
npm install
```

Set up environment variables:

```bash
cp .env.example .env.local
# Configure API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🏃‍♂️ Usage

### A) Running the Indexing

To build the search index from the dataset (this may take some time depending on dataset size):

```bash
# From the backend-python directory
python main.py
```

This script (`main.py`) runs `iterate_dataset` to process the CSV data and `create_inverted_index` to build the inverted index barrels.

### B) Running the Application

**Start the Backend Server:**

```bash
# From the backend-python directory
uvicorn backend:app --reload
```

The API will be available at `http://localhost:8000`.

**Start the Frontend Application:**

```bash
# From the frontend-next directory
npm run dev
```

The UI will be available at `http://localhost:3000`.

### C) Scraping Medium Articles

The application supports real-time scraping and indexing of individual Medium articles.

**Via the User Interface:**

1. Open the application in your browser.
2. Use the "Upload URL" feature.
3. Paste a Medium article URL.
4. The system will scrape the content, process it, and add it to the index in real-time.

**Via API:**
You can also trigger scraping programmatically by sending a POST request to `/upload-url` with the article URL.

## 🏗️ Architecture

### Backend (FastAPI)

- **Search Engine**: Custom implementation based on Google's foundational research
- **Inverted Index**: Barrel-based storage system for efficient retrieval
- **BM25 Scoring**: Advanced relevance ranking with configurable parameters
- **Multi-threading**: Parallel processing for index operations and scoring
- **RESTful API**: Clean endpoints for search, upload, and summarization

### Frontend (Next.js)

- **Modern UI**: Responsive design with smooth animations
- **Real-time Updates**: Live search status and progress indicators
- **Interactive Features**: AI summary toggle, sorting controls
- **Optimized Performance**: Client-side caching and efficient rendering

## 📊 Dataset

- **Source**: Kaggle Medium Articles Dataset
- **Volume**: 190,000+ articles
- **Coverage**: Diverse topics across Medium's ecosystem
- **Preprocessing**: Cleaned, tokenized, and indexed using NLTK

## Configuration

### BM25 Parameters

```python
k = 1.5          # Term frequency saturation parameter
b = 0.75         # Field length normalization
TITLE_VAR = 12   # Title field boost
AUTHOR_VAR = 6   # Author field boost
TAG_VAR = 8      # Tag field boost
```

### Search Features

- **Multi-field Search**: Searches across title, content, tags, and authors
- **Query Preprocessing**: Tokenization, lemmatization, and stop word removal
- **Result Ranking**: Intersection boosting and field-specific scoring
- **Performance**: Thread-based parallel processing

### Scoring Formula

```
BM25 = IDF × (TF × (k + 1)) / (TF + k × (1 - b + b × (|d| / avgdl)))
```

With additional boosters for:

- Query term intersection
- Title matches
- Author relevance
- Tag matches

## 📚 API Endpoints

### Search

```http
POST /search
Content-Type: application/json

{
  "query": "machine learning"
}
```

### Add Article

```http
POST /upload-url
Content-Type: application/json

{
  "url": "https://medium.com/article-url"
}
```

### Generate Summary

```http
POST /summarize
Content-Type: application/json

{
  "wait_for_results": true,
  "max_wait_seconds": 30,
  "summary_length": "short"
}
```

### Summarize Specific Article

```http
POST /summarize-article
Content-Type: application/json

{
  "url": "https://medium.com/article-url",
  "summary_length": "medium"
}
```

## 🤖 AI Integration

### Gemini RAG Module

- **Context Processing**: Intelligent content extraction
- **Summary Generation**: Configurable length summaries
- **Error Handling**: Graceful fallbacks

### Summary Types

- **Short**: Concise overview (1-2 paragraphs)
- **Medium**: Detailed analysis (3-4 paragraphs)
- **Long**: Comprehensive summary (5+ paragraphs)

## 📈 Performance

- **Search Speed**: Sub-second response times
- **Concurrent Users**: Multi-threaded request handling
- **Index Size**: Optimized barrel-based storage
- **Memory Usage**: Efficient data structures and caching

## 🤝 Contributing

All contributions are greatly appreciated!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Project contributors [Ahmad Shahmeer](https://github.com/Sys-Omertosa) & [Sikander Hayat Khan](https://github.com/Sikander-Hayat-Khan) for their help in developing v1 of the search engine
- [The Anatomy of a Large-Scale Hypertextual
  Web Search Engine](http://infolab.stanford.edu/pub/papers/google.pdf)
- Kaggle [Medium Articles Dataset](https://www.kaggle.com/datasets/fabiochiusano/medium-articles)
- FastAPI and Next.js communities
- Google Gemini AI for summarization

---

Built with ❤️ for the Medium community
