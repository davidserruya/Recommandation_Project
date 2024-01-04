import pandas as pd 
import numpy as np 
from scipy.sparse import csr_matrix

def load_data(path: str, chunk_size: int):
    '''
    This function returns a dataframe generated from a csv file path as input

    Args:
    - path : the path where the csv file is located, as a string type
    - chunk_size : number of lines to read from the file per chunk, as an int type

    Returns:
    - df : the dataframe loaded from the csv file

    '''

    data = pd.read_csv(path, iterator=True, chunksize=chunk_size)
    df = df = pd.concat(data, ignore_index=True)

    return df

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

    N = df['userId'].nunique()
    M = df['movieId'].nunique()

    map_user = dict(zip(np.unique(df['userId']), list(range(df['userId'].nunique()))))
    map_movie = dict(zip(np.unique(df['movieId']), list(range(df['movieId'].nunique()))))

    user_idx = [map_user[i] for i in df['userId']]
    movie_idx = [map_movie[i] for i in df['movieId']]

    matrix = csr_matrix((df["rating"], (user_idx, movie_idx)), shape=(N,M))

    df_matrix = df.pivot(index='userId', columns='movieId', values='rating').fillna(0)

    return matrix, df_matrix, map_user, map_movie