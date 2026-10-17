import os
import time
import pickle
import pandas as pd
import requests
import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for styling movie cards & layout
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff4b4b, #ff7b7b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #9ca3af;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .movie-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 8px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .movie-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 10px 15px -3px rgba(255, 75, 75, 0.3);
    }
    .movie-poster-img {
        width: 100%;
        border-radius: 8px;
        aspect-ratio: 2/3;
        object-fit: cover;
    }
    .movie-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f3f4f6;
        height: 2.6rem;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-top: 8px;
        line-height: 1.3rem;
    }
    .movie-meta {
        font-size: 0.8rem;
        color: #fbbf24;
        margin-top: 4px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOVIES_FILE = os.path.join(BASE_DIR, "movies_dict.pkl")
SIMILARITY_FILE = os.path.join(BASE_DIR, "similarity.pkl")
PLACEHOLDER_POSTER = "https://placehold.co/500x750/1e293b/e2e8f0?text=No+Poster"
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

# Cache data loading so it only loads once into memory
@st.cache_data
def load_data():
    with open(MOVIES_FILE, "rb") as f:
        movies_data = pickle.load(f)
    movies_df = pd.DataFrame(movies_data)
    
    with open(SIMILARITY_FILE, "rb") as f:
        similarity_matrix = pickle.load(f)
        
    return movies_df, similarity_matrix

# Cached movie poster and info fetcher
@st.cache_data(show_spinner=False)
def fetch_movie_details(movie_id):
    """
    Fetch poster and metadata from TMDb.
    Uses api.tmdb.org as primary to bypass ISP blocks on api.themoviedb.org.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Try api.tmdb.org first, then api.themoviedb.org
    hosts = ["api.tmdb.org", "api.themoviedb.org"]
    
    for host in hosts:
        url = f"https://{host}/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        try:
            response = requests.get(url, headers=headers, timeout=6)
            if response.status_code == 200:
                data = response.json()
                poster_path = data.get("poster_path")
                vote = data.get("vote_average")
                release_date = data.get("release_date", "")
                year = release_date[:4] if release_date else ""
                
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else PLACEHOLDER_POSTER
                return {
                    "poster": poster_url,
                    "rating": round(vote, 1) if vote else None,
                    "year": year
                }
        except Exception:
            continue
            
    return {"poster": PLACEHOLDER_POSTER, "rating": None, "year": ""}

def recommend(movie_name, movies_df, similarity_matrix, num_recommendations=5):
    """Recommend movies similar to the selected movie."""
    try:
        idx_matches = movies_df[movies_df['title'] == movie_name].index
        if len(idx_matches) == 0:
            return []
        idx = idx_matches[0]
        distances = sorted(list(enumerate(similarity_matrix[idx])), reverse=True, key=lambda x: x[1])
        
        recommendations = []
        for i in distances[1:num_recommendations + 1]:
            movie_id = movies_df.iloc[i[0]]['id']
            title = movies_df.iloc[i[0]]['title']
            details = fetch_movie_details(movie_id)
            recommendations.append({
                "title": title,
                "poster": details["poster"],
                "rating": details["rating"],
                "year": details["year"]
            })
            
        return recommendations
    except Exception as e:
        st.error(f"Error computing recommendations: {e}")
        return []

# App Header
st.markdown("<h1 class='main-title'>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Select your favorite movie and get intelligent Machine Learning recommendations</p>", unsafe_allow_html=True)

# Load datasets
try:
    with st.spinner("Loading movie database..."):
        movies, similarity = load_data()
except Exception as e:
    st.error(f"Failed to load dataset files: {e}")
    st.stop()

# Selection Row
col_select, col_slider = st.columns([3, 1])

with col_select:
    movie_list = movies['title'].values
    # Default selection to a popular movie if available
    default_index = int(movies[movies['title'] == 'Avatar'].index[0]) if 'Avatar' in movie_list else 0
    selected_movie = st.selectbox(
        "🔍 Type or select a movie from the dropdown:",
        options=movie_list,
        index=default_index
    )

with col_slider:
    num_recommendations = st.slider(
        "Recommendations Count:",
        min_value=3,
        max_value=10,
        value=5,
        step=1
    )

# Recommend Button
if st.button("🍿 Recommend Movies", use_container_width=True, type="primary"):
    with st.spinner(f"Analyzing tags & finding recommendations for '{selected_movie}'..."):
        # Fetch selected movie's details
        selected_id = movies[movies['title'] == selected_movie].iloc[0]['id']
        selected_info = fetch_movie_details(selected_id)
        
        # Fetch recommendations
        results = recommend(selected_movie, movies, similarity, num_recommendations)
    
    # Display Selected Movie Info
    st.write("---")
    st.markdown("### 📌 Selected Movie")
    sel_col1, sel_col2 = st.columns([1, 4])
    with sel_col1:
        st.image(selected_info["poster"], use_container_width=True)
    with sel_col2:
        st.markdown(f"## **{selected_movie}**")
        rating_text = f"⭐ {selected_info['rating']} / 10" if selected_info['rating'] else ""
        year_text = f"📅 {selected_info['year']}" if selected_info['year'] else ""
        st.markdown(f"**{rating_text} &nbsp;|&nbsp; {year_text}**")
        st.info("Here are movies similar to your selection based on genre, cast, crew, and plot keywords.")

    st.write("---")
    st.markdown(f"### 🎯 Top {len(results)} Recommended Movies:")
    
    # Render recommendations in responsive columns
    cols = st.columns(len(results))
    for col, item in zip(cols, results):
        with col:
            # Fallback-safe image rendering
            try:
                st.image(item["poster"], use_container_width=True)
            except Exception:
                st.markdown(
                    f'<img src="{item["poster"]}" class="movie-poster-img" alt="{item["title"]}"/>',
                    unsafe_allow_html=True
                )
            
            # Title & Metadata
            st.markdown(f"<div class='movie-title' title='{item['title']}'>{item['title']}</div>", unsafe_allow_html=True)
            meta_parts = []
            if item["rating"]:
                meta_parts.append(f"⭐ {item['rating']}")
            if item["year"]:
                meta_parts.append(f"{item['year']}")
            if meta_parts:
                st.markdown(f"<div class='movie-meta'>{' • '.join(meta_parts)}</div>", unsafe_allow_html=True)
