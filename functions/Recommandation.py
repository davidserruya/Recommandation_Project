import pandas as pd 
import numpy as np
from scipy.sparse.linalg import svds

from functions.Databases import load_data, create_matrix

import spacy
# import xx_ent_wiki_sm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import pickle

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


def generate_reco(df, user_id: int, n_recommandations: int, n_factors:50):
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

    recommandations = list(df[['movieId']].drop_duplicates(subset=['movieId']).set_index('movieId').iloc[reco_movies].index)
    
    return recommandations

def train_model(df, n_recommendations: int):

    '''
    This function retruns a pickle containing a NLP model trained on the list of movies synopsis

    Args:
    - df : a Dataframe containing at least the columns movieId, title and synopsis
    - n_recommandations : the number of movies we want to recommand to the user

    Returns:
    - A pickle named nlp_model
    - A pickle named vectorizer
    '''

    model = spacy.load("xx_ent_wiki_sm")

    synopsis = list(df['Synopsis'])
    vectorizer = TfidfVectorizer(stop_words="english")
    synopsis_tfidf = vectorizer.fit_transform(synopsis)

    nn = NearestNeighbors(n_neighbors=n_recommendations)
    nn.fit(synopsis_tfidf)

    nlp_name = 'nlp_model'
    vec_name = 'vectorizer'
    
    return pickle.dump(nn, open(nlp_name, 'wb')), pickle.dump(vectorizer, open(vec_name, 'wb'))


def nlp_reco(prompt: str, nlp_model_name: str, vector_name: str, df):
    '''
    This function returns a dataframe with a selection of movies recommandations based on user's specific text input

    Args: 
    - prompt : the user's text input describing the kind of movies he wants to see
    - nlp_model_name : the name of the NLP model trained and contained in the pickle (nlp_model in our case)
    - vector_name : the name of the vectorizer trained and contained in the pickle (vectorizer in our case)
    - df : a Dataframe containing at least the columns movieId, title and synopsis

    Returns:
    - reco : a dataframe containing the movie_id, the titles and the genres of the movies we recommand to the user
    
    '''

    model = spacy.load("xx_ent_wiki_sm")
    nlp_model = pickle.load(open(nlp_model_name, 'rb'))
    vectorizer = pickle.load(open(vector_name, 'rb'))

    prompt_doc = model(prompt)
    prompt_tfidf = vectorizer.transform([prompt])

    reco_idx = nlp_model.kneighbors(prompt_tfidf, return_distance=False)[0]

    reco = df.set_index('movieId').iloc[reco_idx].sort_index()

    return reco
