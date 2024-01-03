import pandas as pd
import numpy as np

from scipy.sparse.linalg import svds 

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text

from sklearn.neighbors import NearestNeighbors

from Databases import *

import pickle


def svd(matrix, n_factors: int):
    """
    This function returns a dataframe with the predicted ratings for all users within the dataframe

    Args:
    - matrix : the sparse user-movie matrix created using the create_matrix function
    - n_factors : the number of factors / rank of the latent matrix for factorization

    Returns:
    - predictions : a DataFrame containing the predicted ratings for all users in the original dataset

    Inspired by the following Git repo : https://github.com/vivdalal/movie-recommender-system
        
    """
    # The following code creates :
    # U : user matrix of dimension (n_users, n_factors)
    # sigma : the diagonal matrix of singular values
    # V_t : the transposed movie matrix of dimension (n_factors, n_movies)
    
    U, sigma, V_t = svds(matrix, k = n_factors)

    sigma = np.diag(sigma)

    pred_ratings = np.dot((U @ sigma), V_t)

    predictions = pd.DataFrame(pred_ratings)

    predictions.rename(columns=dict(zip(predictions.columns, list(map_movie.keys()))))
    predictions.index = list(map_user.keys())
    
    return predictions


def recommend_movies(df_pred, user_id: int, df, df_matrix, n_recommendations: int):

    """
    This function returns a DataFrame with movies recommandations based on user's previously rated movies

    Args:
    - df_pred : the dataframe with the rating predictions for all users in the dataset
    - user_id : the user id of the user we want to make recommandations to
    - df : a Dataframe that contains at least the columns movieId, userId, and rating (db_preprocessing) 
    - df_matrix : the user-movie matrix containing the ratings 
    - n_recommandations : the number of movies we want to recommand to the user

    Returns:
    - recommandations : a dataframe containing the movie_id and the titles of the movies we recommand to the user

    Inspired by the following Git repo : https://github.com/vivdalal/movie-recommender-system

    """

    # Sort user's predictions
    sort_pred = df_pred.iloc[user_id].sort_values(ascending=False)
    
    # User data
    user_data = df_matrix.iloc[user_id]

    # Get the index of movies already seen by user
    # We filled by 0 the missing values and there was no 0 rating in the original database
    seen_movies = list(user_data[user_data != 0.0].index)
    
    # Recommend the highest predicted rating movies that the user hasn't seen yet
    reco_movies = sort_pred[~sort_pred.index.isin(seen_movies)][:n_recommendations].index

    # Return the recommanded movies with their respective titles
    recommandations = df[['movieId', 'title']].drop_duplicates(subset=['movieId']).set_index('movieId').iloc[reco_movies]

    return recommandations


def generate_reco(df, user_id: int, n_recommandations: int):
    '''
    This function automates the collaborative filtering recommandations
    '''
    matrix, df_matrix, _, map_movie = create_matrix(df)

    df_pred = svd(matrix, 50).iloc[user_id].sort_values(ascending=False)

    user_data = df_matrix.iloc[user_id]

    seen_movies = list(user_data[user_data != 0.0].index)
    
    reco_movies = df_pred[~df_pred.index.isin(seen_movies)][:n_recommendations].index

    recommandations = df[['movieId', 'title']].drop_duplicates(subset=['movieId']).set_index('movieId').iloc[reco_movies]
    
    return recommandations


def train_model(model_url: str, df, n_recommendations: int):

    '''
    This function retruns a pickle containing a NLP model trained on the list of movies synopsis

    Args:
    - model_url : the url of the type of model (encoder) we want to use to make NLP recommandations
    - df : a Dataframe containing at least the columns movieId, title and synopsis (db_nlp)
    - n_recommandations : the number of movies we want to recommand to the user

    Returns:
    - A pickle named nlp_model

    Inspired by the follwing repo : https://github.com/pritishmishra703/Recommendation-System-with-Universal-Sentence-Encoder
    
    '''

    model = hub.load(model_url)

    synopsis = list(df['Synopsis'])
    
    synop_embed = model([synopsis])

    nn = NearestNeighbors(n_neighbors=n_recommendations)
    nn.fit(synop_embed)

    filename = 'nlp_model'

    return pickle.dump(nn, open(filename, 'wb'))




def nlp_reco(prompt: str, model_url: str, model_name: str, df):
    '''
    This function returns a dataframe with a selection of movies recommandations based on user's specific text input

    Args: 
    - prompt : the user's text input describing the kind of movies he wants to see
    - model_url : the url of the type of model (encoder) we want to use to make NLP recommandations
    - model_name : the name of the NLP model trained and contained in the pickle (nlp_model in our case)
    - df : a Dataframe containing at least the columns movieId, title and synopsis (db_nlp)

    Returns:
    - reco : a dataframe containing the movie_id, the titles and the genres of the movies we recommand to the user


    Inspired by the follwing repo : https://github.com/pritishmishra703/Recommendation-System-with-Universal-Sentence-Encoder
    
    '''

    model = hub.load(model_url)

    nlp_model = pickle.load(open(model_name, 'rb'))

    prompt_embed = model([prompt])

    reco_idx = nlp_model.kneighbors(prompt_embed, return_distance=False)[0]

    reco = df[['title']].iloc[reco_idx].sort_index()

    return reco