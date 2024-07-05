import streamlit as st
import pickle
import pandas as pd
import numpy as np
import requests
import json
import os
from PIL import Image
import zipfile
import io

def load_config(config_file="config.json"):
    config_path = os.path.join(os.path.dirname(__file__),config_file)
    # st.write(config_path)
    try:
        with open(config_path,"r") as f:
            config_data = json.load(f)
        return config_data
    except:
        raise FileNotFoundError(f"Config file'{config_file}'not found")

api_key = (load_config()["TMDB_API_TOKEN"])

movies_list = pickle.load(open('movies.pkl','rb'))

# Unzip and load sim_matrix.pkl
with zipfile.ZipFile('sim_matrix.zip', 'r') as zip_ref:
    with zip_ref.open('sim_matrix.pkl') as file:
        sim_matrix = pickle.load(io.BytesIO(file.read()))

movie_ids = movies_list['id'].values
movies_list = movies_list['title_x'].values


st.title('Movie Recommender System')

def return_img(id):
    img_base_url = "https://image.tmdb.org/t/p/w185/"
    url = "https://api.themoviedb.org/3/movie/{}?language=en-US"
    id = id

    auth = f"Bearer {api_key}"

    headers = {
        "accept": "application/json",
        "Authorization": auth
    }

    response = requests.get(url.format(id), headers=headers)

    response = response.json()

    poster_path =''
    try:
        poster_path =str(response['poster_path'])
        poster_path = img_base_url+poster_path
    except:
        pass

    return poster_path



selected_movie_name = st.selectbox(
'What movie do you want to find similar recommendations of?',
movies_list)

selected_movie_num = st.slider("How many movies to recommend?", 1, 100, 10)

# st.write("Number of movies to recommend: ",selected_movie_num)

def find_movie_index(movie):
     for j,i in enumerate(movies_list):
          if i==movie:
               return j

def recommend(movie,num_movies=5):
    movie_index = find_movie_index(movie)
    distances = sim_matrix[movie_index]
    movies_list_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:num_movies+1] # start from 1 index to exclude movie itself
    M = []
    for i in movies_list_indices:
        M.append(i[0])
    L = []
    for i in M:
        L.append(movies_list[i])
    N = []
    for i in M:
        N.append(movie_ids[i])

    return L,N

# st.write(recommend(selected_movie_name,selected_movie_num))

rec_movies_name , rec_movies_index = recommend(selected_movie_name,selected_movie_num)

if st.button('Recommend'):
    cols = 2
    num_movies = int(selected_movie_num)
    rem = num_movies%cols
    counter=0
    for i in range(0, num_movies-rem, cols):
        row = st.columns(cols)
        for j,col in enumerate(row):
            title = col.container(border=True, height = 400)
            title.header(rec_movies_name[j+counter*cols])
            try:
                title.image(return_img(rec_movies_index[j+counter*cols]))
            except:
                pass
            
        counter = counter+1

    if rem>0:
        last_row = st.columns(rem)
        for j,col in enumerate(last_row):
            title = col.container(border=True, height = 400)
            title.header(rec_movies_name[num_movies-rem+j])
            title.image(return_img(rec_movies_index[num_movies-rem+j]))
        