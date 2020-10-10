from typing import Iterable
import random

from movie_web_app.adapters.repository import AbstractRepository
from movie_web_app.domainmodel.model import Movie


def get_genre_names(repo: AbstractRepository):
    genres = repo.get_genre_list()
    genre_name = [genre.genre_name for genre in genres]
    return genre_name


def get_random_movies(quantity, repo: AbstractRepository):
    movie_count = repo.get_number_of_movies()

    if quantity >= movie_count:
        # Reduce the quantity of ids to generate if the repository has an insufficient number of articles.
        quantity = movie_count - 1

    # Pick distinct and random articles.
    random_ids = random.sample(range(1, movie_count), quantity)
    movies = repo.get_movies_by_id(random_ids)

    return movies_to_dict(movies)


# ============================================
# Functions to convert dicts to model entities
# ============================================

def movie_to_dict(movies: Movie):
    movie_dict = {
        'year': movies.year,
        'title': movies.title
        # 'image_hyperlink': movies.image_hyperlink
    }
    return movie_dict


def movies_to_dict(movies: Iterable[Movie]):
    return [movie_to_dict(movies) for movies in movies]
