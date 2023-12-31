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

@st.cache_resource()
def init_resource():
    model_url = 'https://www.kaggle.com/models/google/universal-sentence-encoder/frameworks/TensorFlow2/variations/multilingual/versions/2'
    model = hub.load(model_url)
    with open('objet_nn.pkl', 'rb') as nn_file:
        nn = pickle.load(nn_file)
    return nn,model

def connect_db():
    try:
        conn = st.connection("postgresql", type="sql")
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

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

def nlp_reco(model,nn,prompt):
    prompt_embed = model([prompt])
    reco_idx = nn.kneighbors(prompt_embed, return_distance=False)[0]
    reco = st.session_state.df_movies.iloc[reco_idx].sort_index()
    return reco