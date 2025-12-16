# Spillage Search - User Manual

This manual provides comprehensive instructions for setting up, running, and using the Spillage Search engine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Git**: Version control system.
- **Git LFS**: Git Large File Storage (required for handling dataset files).
- **Python**: Version 3.8 or higher.
- **Node.js**: Version 18 or higher.
- **npm** or **yarn**: Package manager for Node.js.

## 📥 1. Cloning the Repository

*Note that the ZIP file provided in the submission has a test dataset provided.*

The repository contains large dataset and index files tracked by Git LFS. To clone the repository **without downloading the large files** (to save bandwidth and disk space initially), use the following command:

### Windows (PowerShell)

```powershell
$env:GIT_LFS_SKIP_SMUDGE=1
git clone https://github.com/bonevane/spillage-search.git
cd spillage-search
```

### Linux / macOS

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/bonevane/spillage-search.git
cd spillage-search
```

> **Note**: If you need the dataset files later to run the indexing process, you can pull them specifically using `git lfs pull`.


## ⚙️ 2. Backend Setup

### A. Navigate to Backend Directory

```bash
cd backend-python
```

### B. Create a Virtual Environment (Recommended)

It is best practice to run Python projects in a virtual environment to isolate dependencies.

**Windows:**

```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### C. Install Dependencies

```bash
pip install -r requirements.txt
```

### D. Configure Environment Variables

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    # On Windows Command Prompt use: copy .env.example .env
    ```
2.  Open `.env` and add your Google Gemini API key:
    ```env
    GEMINI_API_KEY=your_actual_api_key_here
    ```

### E. Download NLTK Resources

The search engine requires specific NLTK data for text processing.

```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
```

### F. Generate ANTLR Parser (If needed)

The project uses ANTLR for query parsing. If the `antlr_generated` folder is missing or you modify the grammar, regenerate the parser:

1.  **Install Java**: Ensure Java (JRE/JDK) is installed and in your PATH.
2.  **Run Generation Command**:

    ```bash
    # Windows
    antlr4 -Dlanguage=Python3 -visitor -no-listener -o antlr_generated grammar/Query.g4

    # Linux/Mac (assuming antlr4 alias is set)
    antlr4 -Dlanguage=Python3 -visitor -no-listener -o antlr_generated grammar/Query.g4
    ```

## 💻 3. Frontend Setup

### A. Navigate to Frontend Directory

Open a new terminal window and navigate to the frontend folder:

```bash
cd frontend-next
```

### B. Install Dependencies

```bash
npm install
```

### C. Configure Environment Variables

1.  Copy the example environment file:
    ```bash
    cp .env.example .env.local
    # On Windows Command Prompt use: copy .env.example .env.local
    ```
2.  Ensure the API URL is correctly set in `.env.local`:
    ```env
    NEXT_PUBLIC_API_URL=http://localhost:8000
    ```

## 🚀 4. Running the Application

### A. Building the Index (Optional)

If you have the dataset (e.g., `medium_articles.csv`) and want to rebuild the search index from scratch:

1.  Ensure the dataset file is present in `backend-python/datasets/`.
2.  Run the indexing script:
    ```bash
    # Inside backend-python/ (with venv activated)
    python main.py
    ```
    _This process iterates through the dataset and creates the inverted index barrels in `backend-python/indexes/`._

### B. Starting the Backend Server

```bash
# Inside backend-python/ (with venv activated)
uvicorn backend:app --reload
```

- The backend API will start at `http://localhost:8000`.
- Swagger API documentation is available at `http://localhost:8000/docs`.

### C. Starting the Frontend Interface

```bash
# Inside frontend-next/
npm run dev
```

- The application will be accessible at `http://localhost:3000`.

## 🔍 5. Using the Application

### Search

1.  Navigate to `http://localhost:3000`.
2.  Enter keywords in the search bar (e.g., "machine learning", "python tutorial").
3.  Press Enter or click the search icon.
4.  Results will appear with titles, descriptions, and relevance scores.

### AI Summarization

1.  Perform a search.
2.  Click the **"Summarize"** button (if available) or view the auto-generated summary at the top of the results.
3.  The system uses Google Gemini to synthesize information from the top search results.

### Scraping & Indexing New Articles

You can add new Medium articles to the search index in real-time.

**Method 1: via UI**

1.  Click the **"Upload URL"** button in the navigation bar.
2.  Paste the full URL of a Medium article.
3.  Click **"Upload"**.
4.  The system will scrape the content and add it to the index immediately.

**Method 2: via API**
Send a POST request:

```bash
curl -X POST "http://localhost:8000/upload-url" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://medium.com/@author/article-slug"}'
```

## ❓ Troubleshooting

- **Missing Dependencies**: Ensure you have activated the virtual environment before running `pip install`.
- **API Connection Error**: Check that the backend server is running on port 8000 and the frontend `.env.local` points to the correct URL.
- **Gemini Error**: Verify your `GEMINI_API_KEY` in `backend-python/.env` is valid.
- **Large File Errors**: If you encounter errors about missing CSV files, you may need to pull the LFS files: `git lfs pull`.
