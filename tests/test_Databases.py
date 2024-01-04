import pytest
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from functions.Databases import create_matrix

def test_create_matrix():
    df = pd.DataFrame({'userId': [1, 2, 3, 4, 6, 3, 12],
                       'movieId': [101, 102, 103, 107, 103, 7689, 972],
                        'rating': [5, 4, 3, 2.5, 3.5, 4, 2.5]})

    matrix, df_matrix, map_user, map_movie = create_matrix(df)

    assert isinstance(df_matrix, pd.DataFrame)
    assert isinstance(matrix, csr_matrix)
    assert matrix.shape[0] == df['userId'].nunique()
    assert matrix.shape[1] == df['movieId'].nunique()

    assert isinstance(map_user, dict)
    assert isinstance(map_movie, dict)

    assert set(map_user.values()) == set(range(df['userId'].nunique()))
    assert set(map_movie.values()) == set(range(df['movieId'].nunique()))




