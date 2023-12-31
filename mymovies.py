import streamlit as st
import pandas as pd
from itertools import cycle
from functions import connect_db, get_my_movies,get_movieId,add_movie,remove_special_characters,add_rating,update_movies

# Settings page
col1, col2, col3 = st.columns(3)
with col2:
    option = st.selectbox('Ajouter un film', [''] + st.session_state.df_movies['Title'].tolist())


# Option Selectbox
if option and get_movieId(st.session_state.df_movies,option) not in st.session_state.df_user['MovieId'].tolist():
    st.session_state.df_user=add_movie(st.session_state.df_user,st.session_state['UserId'],get_movieId(st.session_state.df_movies,option))   

# Settings movies presentation
cols = cycle(st.columns(6))
df_user_movie= pd.merge(st.session_state.df_user,st.session_state.df_movies, on='MovieId', how='left')

# loop for showing all movies user
for index in range(len(df_user_movie)):
    # recuperate the movie
    row = df_user_movie.iloc[index]
    col = next(cols)
    # Image
    img_markdown = f"<a href='https://www.imdb.com/search/title/?title={remove_special_characters(row['Title'])}'><img src='{row['Affiche']}' width={200}></a><figcaption>{row['Title']}</figcaption>"
    col.markdown(img_markdown, unsafe_allow_html=True)
    # Slider rating
    rating_key = f'rating_{index}'
    default_value = row['Rating']
    rating= col.slider(f"Note", min_value=0.0, max_value=5.0, value=default_value, key=rating_key, step=0.5) 
    # Add or change the rating
    if rating != row['Rating']:
        st.session_state.df_user=add_rating(st.session_state.df_user,row,rating)


# Update BDD
if st.button("Sauvegarder Films"):
    update_movies(st.session_state.df_user)