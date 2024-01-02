import streamlit as st
from passlib.hash import pbkdf2_sha256
from sqlalchemy import text
import pandas as pd
import string
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text
from sklearn.neighbors import NearestNeighbors
import pickle
from collections import Counter
import random
import spacy
nlp = spacy.load("fr_core_news_sm")
import numpy as np


############################################ INSCRIPTION/CONNEXION/INITIALISATION #####################################

@st.cache_resource()
def init_resource():
    model_url = 'https://www.kaggle.com/models/google/universal-sentence-encoder/frameworks/TensorFlow2/variations/multilingual/versions/2'
    model = hub.load(model_url)
    with open('csv/objet_nn.pkl', 'rb') as nn_file:
        nn = pickle.load(nn_file)
    return nn,model

def connect_db():
    try:
        conn = st.connection("postgresql", type="sql")
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

def capitalize_first_letter(s):
    return s.capitalize()

# Fonction pour vérifier les informations de connexion
def check_credentials(username, password):
    conn = connect_db()
    if conn is None:
        return False
    try:
        result = conn.query("""SELECT * FROM "Users" WHERE "Username"=:username;""",ttl=0, params={"username": username})
        if len(result) > 0:
            if pbkdf2_sha256.verify(password, result['Password'].iloc[0]):
                st.session_state["authentication_status"] = True
                st.session_state["Username"] = result['Username'].iloc[0]
                st.session_state["UserId"] = result['UserId'].iloc[0]
                return True
            else:
                st.session_state["authentication_status"] = 'Password'
                return False
        else:
            st.session_state["authentication_status"] = 'Username'
            return False
    except Exception as e:
        st.error(f"Error checking credentials: {e}")
        return False

# Fonction pour ajouter un utilisateur
def add_user(username, password):
    conn = connect_db()
    if conn is None:
        return False

    try:
        result = conn.query("""SELECT * FROM "Users" WHERE "Username"=:username;""",ttl=0, params={"username": username})
        if len(result) > 0:
            conn.reset()
            return False
        else:
            with conn.session as session:
                try:
                    session.execute(text("""INSERT INTO "Users" ("Username", "Password") VALUES (:username, :password);"""),{"username": username, "password": pbkdf2_sha256.hash(password)})
                    session.commit()
                    session.reset()
                    return True
                except Exception as e:
                    st.error(f"Error adding user: {e}")
                    session.rollback()
                    session.reset()
                    return False
    except Exception as e:
        st.error(f"Error checking existing user: {e}")
        return False

def deconnexion():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.session_state["authentication_status"]=False
    st.experimental_rerun()

############################################ MY MOVIES #####################################

def get_my_movies(userId):
    conn = connect_db()
    if conn is None:
        return False
    try:
        result = conn.query("""SELECT * FROM "Ratings" WHERE "UserId"=:userid;""",ttl=0, params={"userid":int(userId)})
        return result
    except Exception as e:
        st.error(f"Error: {e}")
        return None  

def get_movieId(df,title):
    result = df.loc[df['Title'] == title, 'MovieId']
    return result.iloc[0]

def add_movie(df_user, userId, movieId):
    new_row = {'UserId': userId, 'MovieId': movieId, 'Rating': 0.0}
    df_new_row = pd.DataFrame([new_row])
    df_user = pd.concat([df_user, df_new_row], ignore_index=True)
    return df_user

def remove_special_characters(input_string):
    translator = str.maketrans('', '', string.punctuation)
    result = input_string.translate(translator)
    return result

def add_rating(df_user,row,rating):
    conditions = (df_user['MovieId'] == row['MovieId']) & (df_user['UserId'] == row['UserId'])
    df_user.loc[conditions, 'Rating'] = rating
    return df_user

def update_movies(df_user):
    conn = connect_db()
    if conn is None:
        return False
    try:
        result = conn.query("""SELECT * FROM "Ratings" WHERE "UserId"=:userid;""",ttl=0, params={"userid":int(st.session_state['UserId'])})
        for index in range(len(df_user)):
            row = df_user.iloc[index]
            if row['MovieId'] not in result['MovieId'].tolist():
                with conn.session as session:
                  try:
                    session.execute(text("""INSERT INTO "Ratings" ("UserId", "MovieId","Rating") VALUES (:userid, :movieid,:rating);"""),{"userid": int(st.session_state['UserId']),'movieid':int(row['MovieId']),'rating':float(row['Rating'])})
                    session.commit()
                    session.reset()
                  except Exception as e:
                    st.error(f"Error adding movie: {e}")
                    session.rollback()
                    session.reset()
            else:
                if not result.isin([row]).all(axis=1).any():
                    with conn.session as session:
                       try:
                         session.execute(text("""UPDATE "Ratings" SET "Rating"=:rating WHERE "UserId"=:userid AND "MovieId"=:movieid;"""),{"rating": float(row['Rating']),'userid':int(row['UserId']),'movieid':int(row['MovieId'])})
                         session.commit()
                         session.reset()
                       except Exception as e:
                         st.error(f"Error adding movie: {e}")
                         session.rollback()
                         session.reset()
        st.success("Films Sauvegardés!")
    except Exception as e:
        st.error(f"Error: {e}")
        return None   

############################################ RECOMMANDATIONS #####################################  

def nlp_reco(model,nn,prompt):
    prompt_embed = model([prompt])
    reco_idx = nn.kneighbors(prompt_embed, return_distance=False)[0]
    reco = st.session_state.df_movies.iloc[reco_idx].sort_index()
    return reco

############################################ PAGE ACCUEIL #####################################

def best_movies(df):
    df_best=df[df['RatingMean']>=4.1]
    return df_best.sample(n=8)
    

def more_genres(df,df_movies):
    df=pd.merge(df, df_movies, on='MovieId', how='left')
    genres=get_all_genres(df)
    best_genre=count_word_max(genres)
    df_best_genre = df_movies[(df_movies['RatingMean'] >= 3.5) & (df_movies['Genres'].str.contains(best_genre))]
    return best_genre,df_best_genre.sample(n=8)

def count_word_max(list):
    occurrences = Counter(list)
    max_occurrences = max(occurrences.values())
    mots_max_occurrences = [mot for mot, occurrences_mot in occurrences.items() if occurrences_mot == max_occurrences]
    return random.choice(mots_max_occurrences)

def get_all_genres(df):
    genres=[]
    final_genres=[]
    for genre in df['Genres']:
        genres.append(genre)
    cleaned_genres = [genre.replace("'", '').replace('[','').replace(']','').split('|') for genre in genres]
    for liste in cleaned_genres:
        for genre in liste:
            final_genres.append(genre)
    return final_genres

def tdidf_recom():
    metrique=loaded_cosine()
    MovieId_select=love_movie(st.session_state.df_user)
    movie_name = st.session_state.df_movies.loc[st.session_state.df_movies['MovieId'] == MovieId_select, 'Title'].values
    idx = st.session_state.df_movies.index[st.session_state.df_movies['MovieId'] == MovieId_select].tolist()[0]
    sim_scores = list(enumerate(metrique[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:9]
    film_indices = [i[0] for i in sim_scores]
    return st.session_state.df_movies.iloc[film_indices],movie_name[0]
    
def love_movie(df):
    df_love = df[df['Rating'] >= 4]
    if len(df_love) == 0:
        df_love = df[df['Rating'] == max(df['Rating'])]
    movie_id = df_love.sample(n=1)['MovieId'].iloc[0]
    return movie_id

@st.cache_resource()
def loaded_cosine():
    with open('csv/cosine_similarity_matrix.pkl', 'rb') as file:
       loaded_cosine = pickle.load(file) 
    return loaded_cosine   


def supprimer_mot_film(phrase): 
    nlp = spacy.load("fr_core_news_sm")
    doc = nlp(phrase)
    phrase_sans_film = " ".join([token.text for token in doc if token.text.lower() != "film"])
    return phrase_sans_film

def extraire_mot_cle(phrase):
    doc = nlp(supprimer_mot_film(phrase))
    mot_cle = None
    for token in doc:
        if token.pos_ in ("NOUN", "ADJ"):
            mot_cle = token.text
            break
    return mot_cle


def get_df_ratings():
    conn = connect_db()
    if conn is None:
        return False
    try:
        result = conn.query("""SELECT * FROM "Ratings";""",ttl=0)
        result_df = pd.concat([st.session_state.df_ratings, result], ignore_index=True)
        return result_df
    except Exception as e:
        st.error(f"Error: {e}")
        return st.session_state.df_ratings



