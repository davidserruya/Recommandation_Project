import pytest
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from Recommandation import svd
from Databases import create_matrix


@pytest.mark.parametrize("n_factors", [5, 10, 20])
def test_svd(n_factors):

    df_test = pd.DataFrame({'userId': [1, 2, 1, 2],
                            'movieId': [101, 102, 101, 102],
                            'rating': [5, 4, 3, 2]})

    matrix = create_matrix(df_test)[0]  

    assert isinstance(matrix, csr_matrix)

    predictions = svd(matrix, n_factors)

    assert isinstance(predictions, pd.DataFrame)
    assert predictions.shape == matrix.shape

    assert set(predictions.columns) == set(range(matrix.shape[1]))
    assert set(predictions.index) == set(range(matrix.shape[0]))
