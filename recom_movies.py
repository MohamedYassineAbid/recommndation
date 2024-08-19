import streamlit as st

# Set the page title and configuration
st.set_page_config(
    page_title="My Movie Recommendation App",  
    page_icon="🎬",  
)

import json
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import difflib
import os

api_key = os.getenv('api_key')
vectorizer = TfidfVectorizer()
data = pd.read_csv('movie_dataset.csv')
data.fillna('', inplace=True)
combined_features = data['genres'] + ' ' + data['keywords'] + ' ' + data['tagline'] + ' ' + data['cast'] + ' ' + data['director'] + ' ' + data['original_language'] + ' ' + data['original_title'] + ' ' + data['production_countries'] + ' ' + data['title']
feature_vectors = vectorizer.fit_transform(combined_features)
similarity = cosine_similarity(feature_vectors)
#display recommmendations
def display_recommendations(recommendations):
    if isinstance(recommendations, str):
        st.error(recommendations)
    else:
        st.subheader("Movies suggested for you:")
        for i, (title, poster_url) in enumerate(recommendations, start=1):
            col1, col2 = st.columns([1, 2])
            with col1:
                if poster_url:
                    st.image(poster_url, width=100)
                else:
                    st.write("No poster available")
            with col2:
                st.write(f"{i}. {title}")

#getting the recommended movie poster

def get_movie_recommendations_with_posters(movie_name):
    if len(movie_name) < 2:
        return "Please enter at least two characters for a meaningful search."
    
    list_of_all_titles = data['title'].tolist()
    find_close_match = difflib.get_close_matches(movie_name, list_of_all_titles)
    if not find_close_match:
        return "No close matches found. Please try a different name."
    
    close_match = find_close_match[0]
    index_of_the_movie = data[data.title == close_match]['index'].values[0]
    similarity_score = list(enumerate(similarity[index_of_the_movie]))
    sorted_similar_movies = sorted(similarity_score, key=lambda x: x[1], reverse=True)
    
    recommendations = []
    for movie in sorted_similar_movies:
        index = movie[0]
        title_from_index = data[data.index == index]['title'].values[0]
        if len(recommendations) < 5:
            recommendations.append(title_from_index)
        else:
            break
    
    movies_with_posters = []
    for title in recommendations:
        poster_url = get_movie_poster(title)
        movies_with_posters.append((title, poster_url))

    return movies_with_posters

#getting movie 's poster from omdb api
def get_movie_poster(movie_title):
    url = f'http://www.omdbapi.com/?apikey={api_key}&t={movie_title}&plot=short&r=json'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'Poster' in data and data['Poster'] != 'N/A':
            return data['Poster']
        else:
            return None
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error fetching poster for {movie_title}: {e}")
        return None

movie_name = st.text_input('Enter your favorite movie name:')
if movie_name:
    recommendations_with_posters = get_movie_recommendations_with_posters(movie_name)
    if isinstance(recommendations_with_posters, str):
        st.error(recommendations_with_posters)
    else:
        display_recommendations(recommendations_with_posters)

st.markdown("By Abidology")
