import pytest
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from Databases import load_data
from Databases import create_matrix

@pytest.mark.parametrize("path, chunk_size", [("db_sample.csv", 100), ("db_nlp", 500)])
def test_load_data():

    assert isinstance(chunk_size, int)
    assert isinstance(path, str)

    df = load_data(path, chunk_size)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


@pytest.mark.parametrize("df", [pd.DataFrame({'userId': [1, 2, 1], 'movieId': [101, 102, 101], 'rating': [5, 4, 3]}),
                                pd.DataFrame({'userId': [1, 2, 3], 'movieId': [101, 102, 103], 'rating': [5, 4, 3]})])

def test_create_matrix(df):
    # Appel de la fonction avec le DataFrame de test
    matrix, df_matrix, map_user, map_movie = create_matrix(df)

    assert isinstance(df_matrix, pd.DataFrame)
    assert isinstance(matrix, csr_matrix)
    assert matrix.shape[0] == df['userId'].nunique()
    assert matrix.shape[1] == df['movieId'].nunique()

    assert isinstance(map_user, dict)
    assert isinstance(map_movie, dict)

    assert set(map_user.values()) == set(range(df['userId'].nunique()))
    assert set(map_movie.values()) == set(range(df['movieId'].nunique()))

