import pytest
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

from functions.Recommandation import svd, generate_reco
from functions.Databases import create_matrix

def test_svd():

    df = pd.DataFrame({'userId': [1, 2, 3, 4, 6, 3, 12],
                       'movieId': [101, 102, 103, 107, 103, 7689, 972],
                        'rating': [5, 4, 3, 2.5, 3.5, 4, 2.5]})
    
    matrix, _, map_user, map_movie = create_matrix(df)

    n_factors = 2

    assert isinstance(matrix, csr_matrix)

    predictions = svd(matrix, map_user, map_movie, n_factors)

    assert isinstance(predictions, pd.DataFrame)
    assert predictions.shape == matrix.shape


def test_generate_reco():

    df = pd.DataFrame({'userId': [1, 2, 3, 4, 6, 3, 12],
                       'movieId': [101, 102, 103, 107, 103, 7689, 972],
                       'rating': [5, 4, 3, 2.5, 3.5, 4, 2.5]})
    nb_factors = 2
    
    recommandations = generate_reco(df, user_id=6, n_recommandations=2, n_factors=nb_factors)

    assert isinstance(recommandations, list)
    assert len(recommandations) == 2







