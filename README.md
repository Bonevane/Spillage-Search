# Spillage Search

Spillage Search is a search engine designed to explore Medium articles.

## Features
-  Over 190k Medium articles indexed for fast search.
- Access it live at [Spillage Search](https://spillage-search.vercel.app/).
- Frontend built with Next.js, with the backend powered by FastAPI

## Dataset
The Medium articles dataset is sourced from Kaggle: [Medium Articles Dataset](https://www.kaggle.com/datasets/fabiochiusano/medium-articles).

Pre-generated indexes are available here: [Indexes](https://drive.google.com/drive/folders/1Mp6EyruvPWoVeRgllPHfM5Id3lgN57t-?usp=sharing).

## Setup Instructions

### Steps

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd spillage-search
   ```

2. **Backend Setup:**
   - Navigate to the `backend-python` directory:
     ```bash
     cd backend-python
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
     Run downloads.py to download necessary NLTK resources:
     ```bash
     python downloads.py
     ```
   - Generate the indexes using `main.py`:
     ```bash
     python main.py
     ```
     Alternatively, download and use the pre-generated indexes linked above.
     
   - Start the backend server:
     ```bash
     uvicorn backend:app --reload
     ```

3. **Frontend Setup:**
   - Navigate to the `frontend-react` directory:
     ```bash
     cd ../frontend-react
     ```
   - Install dependencies:
     ```bash
     npm install
     ```
   - Start the development server:
     ```bash
     npm run dev
     ```

4. Open your browser and navigate to `http://localhost:3000` to access Spillage Search locally.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
Special thanks to:
- [Kaggle](https://www.kaggle.com/) for providing the dataset.
- All contributors who made this project possible.
