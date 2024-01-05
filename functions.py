import streamlit as st
from passlib.hash import pbkdf2_sha256
from sqlalchemy import text
import pandas as pd
import string
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import pickle
from collections import Counter
import random
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
import numpy as np
import fr_core_news_md
nlp = fr_core_news_md.load()
from spacy.lang.en.stop_words import STOP_WORDS
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
from sentence_transformers import SentenceTransformer, util
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
nltk.download('punkt')


############################################ INSCRIPTION/CONNEXION/INITIALISATION #####################################

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
                    st.balloons()
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
def preprocess_text(text):

    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    filtered_words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]
    
    return ' '.join(filtered_words)


def nlp_reco(prompt: str, df, n_recommendations: int):
    '''
    This function returns a dataframe with a selection of movies recommandations based on user's specific text input

    Args: 
    - prompt : the user's text input describing the kind of movies he wants to see
    - df : a Dataframe containing at least the columns movieId, title and synopsis
    - n_recommandations : the number of movies we want to recommand to the user

    Returns:
    - reco : a dataframe containing the movie_id, the titles and the genres of the movies we recommand to the user
    
    '''
    model = spacy.load("xx_ent_wiki_sm")
 
    vectorizer = TfidfVectorizer(stop_words="english")

    synopsis_tfidf = vectorizer.fit_transform(df['Synopsis'])

    nn = NearestNeighbors(n_neighbors=n_recommendations)
    nn.fit(synopsis_tfidf)

    prompt_doc = model(prompt)
    prompt_text = preprocess_text(prompt_doc.text)
    prompt_tfidf = vectorizer.transform([prompt_text])

    reco_idx = nn.kneighbors(prompt_tfidf, return_distance=False)[0]

    reco = df[['MovieId', 'Title', 'Genres', 'Synopsis','Affiche']].set_index('MovieId').iloc[reco_idx].sort_index()

    return pd.DataFrame(reco)

############################################ PAGE ACCUEIL #####################################

def best_movies(df):
    df_best=df[df['RatingMean']>=4.1]
    return df_best.sample(n=8)
    

def more_genres(df,df_movies):
    df=pd.merge(df, df_movies, on='MovieId', how='left')
    genres=get_all_genres(df)
    best_genre=count_word_max(genres)
    df_best_genre = df_movies[(df_movies['RatingMean'] >= 3.5) & (df_movies['Genres'].str.contains(best_genre))]
    if len(df_best_genre)<8:
        df_best_genre=df_movies[df_movies['Genres'].str.contains(best_genre)]
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
    genres_concatenes = ",".join(final_genres)
    liste_unique = [genre.strip() for genre in genres_concatenes.split(",")]
    return liste_unique

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

def create_matrix(df):
    """
    This function creates a sparse user-movie matrix from a dataframe

    Args:
    - a Dataframe that contains at least the columns movieId, userId, and rating (db_preprocessing)

    Returns:
    - matrix : a sparse user-movie matrix of size NxM with N the number of unique users and M the number of unique movies
    - map_user : a dictionary that maps user_ids to their respective indices
    - map_user_inv : a dictionary that maps indices to the user_id
    - map_movie : a dictionary that maps movie_ids to their respective indices
    - map_movie_inv : a dictionary that maps indices to the movie_id

    Inspired by the following repo : https://github.com/topspinj/tmls-2020-recommender-workshop
    """

    N = df['UserId'].nunique()
    M = df['MovieId'].nunique()

    map_user = dict(zip(np.unique(df['UserId']), list(range(df['UserId'].nunique()))))
    map_movie = dict(zip(np.unique(df['MovieId']), list(range(df['MovieId'].nunique()))))

    user_idx = [map_user[i] for i in df['UserId']]
    movie_idx = [map_movie[i] for i in df['MovieId']]

    matrix = csr_matrix((df["Rating"], (user_idx, movie_idx)), shape=(N,M))

    df_matrix = df.pivot(index='UserId', columns='MovieId', values='Rating').fillna(0)

    return matrix, df_matrix, map_user, map_movie

def svd(matrix, map_user: dict, map_movie: dict, n_factors: int):
    """
    This function returns a dataframe with the predicted ratings for all users within the dataframe

    Args:
    - matrix : the sparse user-movie matrix created using the create_matrix function
    - n_factors : the number of factors / rank of the latent matrix for factorization
    - map_user : a dictionary that maps user_ids to their respective indices
    - map_movie : a dictionary that maps movie_ids to their respective indices

    Returns:
    - predictions : a DataFrame containing the predicted ratings for all users in the original dataset

    Inspired by the following Git repo : https://github.com/vivdalal/movie-recommender-system
        
    """
    # The following code creates :
    # U : user matrix of dimension (n_users, n_factors)
    # sigma : the diagonal matrix of singular values
    # V_t : the transposed movie matrix of dimension (n_factors, n_movies)
    
    try:

        U, sigma, V_t = svds(matrix, k = n_factors)

        sigma = np.diag(sigma)

        pred_ratings = np.dot((U @ sigma), V_t)

        predictions = pd.DataFrame(pred_ratings)

        predictions.rename(columns=dict(zip(predictions.columns, list(map_movie.keys()))), inplace=True)
        predictions.index = list(map_user.keys())
    
    except ValueError:
        print('The number of factor ({0}) is either smaller than 1 or larger than one dimension of \
              the matrix shape ({1})'.format(n_factors, matrix.shape))
    
    return predictions

def collab_reco(df, user_id: int, n_recommandations: int, n_factors:50):
    """
    This function returns a DataFrame with movies recommandations based on user's previously rated movies

    Args:
    - df : a Dataframe that contains at least the columns movieId, userId, and rating
    - user_id : the user id of the user we want to make recommandations to
    - n_recommandations : the number of movies we want to recommand to the user
    - n_factors : the number of factors / rank of the latent matrix for factorization (default is 50)

    Returns:
    - recommandations : a list containing the movie_id of the movies we recommand to the user

    Inspired by the following Git repo : https://github.com/vivdalal/movie-recommender-system
    """

    matrix, df_matrix, map_user, map_movie = create_matrix(df)

    df_pred = svd(matrix, map_user, map_movie, n_factors).loc[user_id].sort_values(ascending=False)

    user_data = df_matrix.loc[user_id]

    seen_movies = list(user_data[user_data != 0.0].index)
    
    reco_movies = df_pred[~df_pred.index.isin(seen_movies)][:n_recommandations].index

    recommandations = list(df[['MovieId']].drop_duplicates(subset=['MovieId']).set_index('MovieId').loc[reco_movies].index)
    
    recommandations=st.session_state.df_movies_light[st.session_state.df_movies_light['MovieId'].isin(recommandations)]

    return recommandations


def supprimer_mot_film(phrase, nlp):
    doc = nlp(phrase)
    phrase_sans_film = " ".join([token.text for token in doc if token.text.lower() != "film"])
    return phrase_sans_film
 
def nettoyer_phrase(phrase, nlp):
    doc = nlp(phrase)
    mots_nettoyes = [token.lemma_ for token in doc if token.text.lower() not in STOP_WORDS and token.is_punct == False]
    return " ".join(mots_nettoyes)
 
def extraire_mots_cles(phrase, nlp, nombre_mots_cles=1, pos=["NOUN", "ADJ"]):
    phrase_modifiee = nettoyer_phrase(supprimer_mot_film(phrase, nlp), nlp)
    doc = nlp(phrase_modifiee)
    mots_cles = []
    for token in doc:
        if token.pos_ in pos and token.text not in mots_cles:
            mots_cles.append(token.text)
            if len(mots_cles) == nombre_mots_cles:
                break
    return mots_cles[0]

