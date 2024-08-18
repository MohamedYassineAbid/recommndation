import json
import requests
import streamlit as st
import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import difflib
import creds
import os
api_key = os.getenv('api_key')
vectorizer = joblib.load('tfidf_vectorizer.pkl')
data = pd.read_csv('movie_dataset.csv')

data.fillna('', inplace=True)
combined_features = data['genres'] + ' ' + data['keywords'] + ' ' + data['tagline'] + ' ' + data['cast'] + ' ' + data['director'] + ' ' + data['original_language'] + ' ' + data['original_title'] + ' ' + data['production_countries'] + ' ' + data['title']
feature_vectors = vectorizer.transform(combined_features)
similarity = cosine_similarity(feature_vectors)

# Streamlit interface
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
def get_movie_recommendations_with_posters(movie_name):
  recommendations = get_movie_recommendations(movie_name)  
  movies_with_posters = []

  for title in recommendations:
    poster_url = get_movie_poster(title)
    movies_with_posters.append((title, poster_url))

  return movies_with_posters    
def get_movie_recommendations(movie_name):
    list_of_all_titles = data['title'].tolist()
    find_close_match = difflib.get_close_matches(movie_name, list_of_all_titles)
    if not find_close_match:
        return "Movie not found in the dataset."
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
    return recommendations

def get_movie_poster(movie_title):
    url = f'http://www.omdbapi.com/?apikey={api_key}&t={movie_title}&plot=short&r=json'

    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = json.loads(response.text)
        if 'Poster' in data and data['Poster'] != 'N/A':
            return data['Poster']
        else:
            return None 
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error fetching poster for {movie_title}: {e}")
        return None  

# Get user input
movie_name = st.text_input('Enter your favorite movie name:')
if movie_name:
  recommendations = get_movie_recommendations_with_posters(movie_name)
  display_recommendations(recommendations)

st.markdown("By Abidology")