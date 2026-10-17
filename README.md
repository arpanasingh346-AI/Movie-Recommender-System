# Movie Recommendation System (ML)

A Machine Learning based Content-Based Movie Recommendation System built using Python, Scikit-learn, and Streamlit. It recommends similar movies along with high-definition posters, ratings, and release years fetched via the TMDb API.

## 🚀 Features

- **Content-Based Filtering**: Calculates cosine similarity across movie tags (genres, keywords, cast, crew, overview).
- **Interactive UI**: Clean, responsive Streamlit dashboard with customizable recommendation count (3 to 10).
- **Movie Posters & Metadata**: Live posters, release years, and TMDb/IMDb ratings.
- **Fast Performance**: In-memory caching (`@st.cache_data`) for instant recommendation lookups.
- **Resilient API Calls**: Automatic failover (`api.tmdb.org` & `api.themoviedb.org`) and placeholder image fallbacks.

## 🛠️ Technologies Used

- **Python** (Pandas, NumPy, Scikit-Learn)
- **Streamlit** (Web Application Interface)
- **TMDb API** (Movie metadata & posters)
- **Pillow** (Image processing)

## 📁 Project Structure

```text
├── App.py                       # Main Streamlit application
├── app (1).py                   # Synchronized application file
├── requirements.txt             # Project dependencies
├── movies_dict.pkl              # Processed movie dataset (dictionary)
├── similarity.pkl               # Precomputed 4806x4806 cosine similarity matrix
├── notebook86c26b4f17.ipynb     # Jupyter Notebook for data processing & model training
├── tmdb_5000_movies.csv         # Kaggle TMDb movies dataset
├── tmdb_5000_credits.csv        # Kaggle TMDb credits dataset
└── README.md                    # Project documentation
```

## ⚙️ How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   streamlit run App.py
   ```

3. Open your browser at `http://localhost:8501`.