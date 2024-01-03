

import pytest
import pandas as pd
from functions import capitalize_first_letter, get_movieId, remove_special_characters, count_word_max, add_rating

# Assuming the module is named 'my_module'

# Test capitalize_first_letter
def test_capitalize_first_letter():
    assert capitalize_first_letter("hello") == "Hello"
    assert capitalize_first_letter("world") == "World"

# Test get_movieId
def test_get_movieId():
    df = pd.DataFrame({'Title': ['Movie1', 'Movie2', 'Movie3', 'Movie4', 'Movie5'], 'MovieId': [1, 2, 3, 4, 5]})
    assert get_movieId(df, 'Movie1') == 1
    assert get_movieId(df, 'Movie2') == 2
    assert get_movieId(df, 'Movie3') == 3
    assert get_movieId(df, 'Movie4') == 4
    assert get_movieId(df, 'Movie5') == 5

# Test remove_special_characters
def test_remove_special_characters():
    assert remove_special_characters("Hello, World!") == "Hello World"
    assert remove_special_characters("1234!@#$") == "1234"

# Test count_word_max
def test_count_word_max():
    word_list = ["apple", "orange", "apple", "banana", "orange", "apple"]
    assert count_word_max(word_list) in ["apple", "orange"]

# Test add_rating
def test_add_rating():
    df_user = pd.DataFrame({'UserId': [1, 2], 'MovieId': [1, 2], 'Rating': [3, 4]})
    row = {'UserId': 1, 'MovieId': 1}
    rating = 5
    new_df_user = add_rating(df_user, row, rating)
    assert new_df_user.loc[(new_df_user['UserId'] == 1) & (new_df_user['MovieId'] == 1), 'Rating'].iloc[0] == 5

if __name__ == "__main__":
    pytest.main()
