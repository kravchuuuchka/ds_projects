#!/usr/bin/env python3

import pytest
from tags import Tags
from movies import Movies as OuterMovies
from links import Links
from ratings import Ratings, average, median

########################################################
################### Tags ###############################
########################################################

@pytest.fixture
def tags():
    return Tags()

def test_tags_most_words(tags):
    result = tags.most_words(5)
    assert isinstance(result, dict)
    assert all(isinstance(k, str) and isinstance(v, int) for k, v in result.items())
    assert list(result.values()) == sorted(result.values(), reverse=True)

def test_tags_longest(tags):
    result = tags.longest(5)
    assert isinstance(result, dict)
    for key, value in result.items():
        assert isinstance(key, str)
        assert isinstance(value, int)
    

def test_tags_most_popular(tags):
    result = tags.most_popular(5)
    assert isinstance(result, dict)
    assert all(isinstance(k, str) and isinstance(v, int) for k, v in result.items())
    assert list(result.values()) == sorted(result.values(), reverse=True)

def test_tags_with_word(tags):
    result = tags.tags_with("war")
    assert isinstance(result, list)
    assert all(isinstance(tag, str) for tag in result)

def test_tags_dist_by_year(tags):
    result = tags.dist_by_year()
    assert isinstance(result, dict)
    assert all(isinstance(k, int) and isinstance(v, int) for k, v in result.items())

###############################################################
####################### Movies ################################
###############################################################

@pytest.fixture
def outer_movies():
    return OuterMovies()

def test_movies_dist_by_release(outer_movies):
    result = outer_movies.dist_by_release()
    assert isinstance(result, dict)
    assert all(k.isdigit() and len(k) == 4 and isinstance(v, int) for k, v in result.items())

def test_movies_dist_by_genres(outer_movies):
    result = outer_movies.dist_by_genres()
    assert isinstance(result, dict)
    assert all(isinstance(k, str) and isinstance(v, int) for k, v in result.items())

def test_movies_most_genres(outer_movies):
    result = outer_movies.most_genres(5)
    assert isinstance(result, dict)
    assert all(isinstance(k, str) and isinstance(v, int) for k, v in result.items())
    assert list(result.values()) == sorted(result.values(), reverse=True)

########################################################
################### Links ##############################
########################################################

@pytest.fixture(scope="session")
def links():
    return Links("./ml-latest-small/links.csv", "./ml-latest-small/movies.csv")

def assert_sorted_desc_dict(d: dict):
    values = list(d.values())
    assert values == sorted(values, reverse=True)

def test_get_imdb_types(links):
    result = links.get_imdb([1, 2, 3], ["title", "budget"])

    assert isinstance(result, list)
    assert all(isinstance(row, list) for row in result)
    assert all(isinstance(row[0], int) for row in result)

def test_get_imdb_fields_types(links):
    result = links.get_imdb([1, 2], ["title", "budget", "runtime"])

    for row in result:
        assert isinstance(row[0], int)
        assert isinstance(row[1], str)
        assert isinstance(row[2], int)
        assert isinstance(row[3], int)

def test_get_imdb_sorted(links):
    result = links.get_imdb([1, 2, 3], ["title"])

    movie_ids = [row[0] for row in result]
    assert movie_ids == sorted(movie_ids, reverse=True)

def test_get_tmdb_types(links):
    result = links.get_tmdb([1, 2], ["title"])

    assert isinstance(result, list)
    assert all(isinstance(row, list) for row in result)

def test_get_tmdb_fields(links):
    result = links.get_tmdb([1, 2], ["title", "budget"])

    for row in result:
        assert isinstance(row[0], int)
        assert isinstance(row[1], str)
        assert isinstance(row[2], int)

def test_get_tmdb_sorted(links):
    result = links.get_tmdb([1, 2, 3], ["title"])

    movie_ids = [row[0] for row in result]
    assert movie_ids == sorted(movie_ids, reverse=True)

def test_top_directors_types(links):
    result = links.top_directors(5)

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result.keys())
    assert all(isinstance(v, int) for v in result.values())

def test_top_directors_sorted(links):
    result = links.top_directors(10)

    values = list(result.values())
    assert values == sorted(values, reverse=True)

def test_top_directors_limit(links):
    result = links.top_directors(3)
    assert len(result) <= 3

def test_top_directors_raise(links):
    with pytest.raises(ValueError):
        links.top_directors(0)

def test_most_expensive_types(links):
    result = links.most_expensive(5)

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)
    assert all(isinstance(v, int) for v in result.values())

def test_most_expensive_sorted(links):
    result = links.most_expensive(10)

    values = list(result.values())
    assert values == sorted(values, reverse=True)

def test_most_expensive_limit(links):
    result = links.most_expensive(2)
    assert len(result) <= 2

def test_most_expensive_raise(links):
    with pytest.raises(ValueError):
        links.most_expensive(-1)

def test_most_profitable_types(links):
    result = links.most_profitable(5)

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)
    assert all(isinstance(v, int) for v in result.values())

def test_most_profitable_sorted(links):
    result = links.most_profitable(10)

    values = list(result.values())
    assert values == sorted(values, reverse=True)

def test_most_profitable_raise(links):
    with pytest.raises(ValueError):
        links.most_profitable(0)

def test_longest_types(links):
    result = links.longest(5)

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)
    assert all(isinstance(v, int) for v in result.values())

def test_longest_sorted(links):
    result = links.longest(10)

    values = list(result.values())
    assert values == sorted(values, reverse=True)

def test_longest_raise(links):
    with pytest.raises(ValueError):
        links.longest(-3)

def test_cost_per_min_types(links):
    result = links.top_cost_per_minute(5)

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)
    assert all(isinstance(v, float) for v in result.values())

def test_cost_per_min_sorted(links):
    result = links.top_cost_per_minute(10)

    values = list(result.values())
    assert values == sorted(values, reverse=True)

def test_cost_per_min_raise(links):
    with pytest.raises(ValueError):
        links.top_cost_per_minute(0)

###############################################################
######################## Ratings ##############################
###############################################################

@pytest.fixture(scope="session")
def ratings():
    return Ratings("./ml-latest-small/ratings.csv", "./ml-latest-small/movies.csv")


@pytest.fixture(scope="session")
def movies(ratings):
    return ratings.movies


@pytest.fixture(scope="session")
def users(ratings):
    return ratings.users

def test_dist_by_year_types(movies):
    result = movies.dist_by_year()

    assert isinstance(result, dict)
    assert all(isinstance(k, int) for k in result)
    assert all(isinstance(v, int) for v in result.values())

def test_dist_by_year_sorted(movies):
    result = movies.dist_by_year()

    keys = list(result.keys())
    assert keys == sorted(keys)

def test_dist_by_rating_types(movies):
    result = movies.dist_by_rating()

    assert isinstance(result, dict)
    assert all(isinstance(k, float) for k in result)
    assert all(isinstance(v, int) for v in result.values())

def test_dist_by_rating_sorted(movies):
    result = movies.dist_by_rating()

    keys = list(result.keys())
    assert keys == sorted(keys)

def test_top_by_num_of_ratings_types(movies):
    result = movies.top_by_num_of_ratings(5)

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)
    assert all(isinstance(v, int) for v in result.values())

def test_top_by_num_of_ratings_sorted(movies):
    result = movies.top_by_num_of_ratings(10)

    values = list(result.values())
    assert values == sorted(values, reverse=True)

def test_top_by_num_of_ratings_limit(movies):
    result = movies.top_by_num_of_ratings(3)
    assert len(result) <= 3

def test_top_by_num_of_ratings_raise(movies):
    with pytest.raises(ValueError):
        movies.top_by_num_of_ratings(0)

def test_top_by_num_of_ratings_key_error(movies):
    with pytest.raises(KeyError):
        movies.top_by_num_of_ratings(3, key="invalid")

def test_top_by_ratings_types(movies):
    result = movies.top_by_ratings(5, metric=average)

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)
    assert all(isinstance(v, float) for v in result.values())

def test_top_by_ratings_median(movies):
    result = movies.top_by_ratings(5, metric=median)

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)
    assert all(isinstance(v, float) for v in result.values())

    values = list(result.values())
    assert values == sorted(values, reverse=True)

def test_top_by_ratings_sorted(movies):
    result = movies.top_by_ratings(10, metric=average)

    values = list(result.values())
    assert values == sorted(values, reverse=True)

def test_top_by_ratings_raise(movies):
    with pytest.raises(ValueError):
        movies.top_by_ratings(0, metric=average)

def test_top_controversial_types(movies):
    result = movies.top_controversial(5)

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)
    assert all(isinstance(v, float) for v in result.values())

def test_top_controversial_sorted(movies):
    result = movies.top_controversial(10)

    values = list(result.values())
    assert values == sorted(values, reverse=True)

def test_users_top_by_num_of_ratings(users):
    result = users.top_by_num_of_ratings(5)

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)
    assert all(isinstance(v, int) for v in result.values())

def test_users_top_by_ratings(users):
    result = users.top_by_ratings(5, metric=average)

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)
    assert all(isinstance(v, float) for v in result.values())

def test_users_top_by_ratings_median(users):
    result = users.top_by_ratings(5, metric=median)

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)
    assert all(isinstance(v, float) for v in result.values())

    values = list(result.values())
    assert values == sorted(values, reverse=True)

def test_users_dist_by_num_of_ratings(users):
    result = users.dist_by_num_of_ratings()

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)
    assert all(isinstance(v, int) for v in result.values())

def test_users_dist_by_ratings_median(users):
    result = users.dist_by_ratings(metric=median)

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)
    assert all(isinstance(v, float) for v in result.values())

    values = list(result.values())
    assert values == sorted(values)

def test_users_dist_by_ratings_sorted(users):
    result = users.dist_by_ratings()

    values = list(result.values())
    assert values == sorted(values)

def test_users_movies_rated_by_user(users):
    user_id = users._data[0]["userId"]
    result = users.movies_rated_by_user(user_id)

    assert isinstance(result, list)
    assert all(isinstance(x, str) for x in result)

def test_users_movies_rated_by_user_raise(users):
    with pytest.raises(ValueError):
        users.movies_rated_by_user("abc123")

def test_users_top_active_by_period(users):
    result = users.top_active_by_period(5, 2015)

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)
    assert all(isinstance(v, int) for v in result.values())

def test_users_top_active_by_period_raise(users):
    with pytest.raises(ValueError):
        users.top_active_by_period(5, "not_year")

def test_top_controversial_variance_logic(movies):
    result = movies.top_controversial(5)

    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)
    assert all(isinstance(v, float) for v in result.values())
    assert all(v >= 0 for v in result.values())