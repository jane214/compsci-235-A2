from typing import List, Iterable

from movie_web_app.adapters.repository import AbstractRepository
from movie_web_app.domainmodel.model import make_review, Movie, Review, Genre


class NonExistentMovieException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def add_comment(movie_id: int, comment_text: str, username: str, repo: AbstractRepository):
    # Check that the movie exists.
    movie = repo.get_movie(int(movie_id))
    if movie is None:
        raise NonExistentMovieException

    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException

    # Create comment.
    comment = make_review(comment_text, user, movie)

    # Update the repository.
    repo.add_comment(comment)


def get_movie(movie_id: int, repo: AbstractRepository):
    movie = repo.get_movie(int(movie_id))

    if movie is None:
        raise NonExistentMovieException

    return movie_to_dict(movie)


def get_first_movie(repo: AbstractRepository):

    movie = repo.get_first_movie()

    return movie_to_dict(movie)


def get_last_movie(repo: AbstractRepository):

    movie = repo.get_last_movie()
    return movie_to_dict(movie)


def get_movies_by_year(year, repo: AbstractRepository):
    # Returns Movies for the target year (empty if no matches), the year of the previous movie (might be null),
    # the date of the next movie (might be null)

    movies = repo.get_movies_by_year(target_year=int(year))

    movies_dto = list()
    prev_year = next_year = None

    if len(movies) > 0:
        prev_year = repo.get_year_of_previous_movie(movies[0])
        next_year = repo.get_year_of_next_movie(movies[0])

        # Convert Movies to dictionary form.
        movies_dto = movies_to_dict(movies)

    return movies_dto, prev_year, next_year


def get_movie_ids_for_genre(genre_name, repo: AbstractRepository):
    movie_ids = repo.get_movie_ids_for_genre(genre_name)

    return movie_ids


def get_movies_by_id(id_list, repo: AbstractRepository):
    movies = repo.get_movies_by_id(id_list)

    # Convert Articles to dictionary form.
    movies_as_dict = movies_to_dict(movies)

    return movies_as_dict


def get_comments_for_movie(movie_id, repo: AbstractRepository):
    movie = repo.get_movie(movie_id)

    if movie is None:
        raise NonExistentMovieException

    return comments_to_dict(movie.reviews)


# ============================================
# Functions to convert model entities to dicts
# ============================================

def movie_to_dict(movie: Movie):
    movie_dict = {
        'id': movie.id,
        'year': movie.year,
        'title': movie.title,
        'description': movie.description,
        'hyperlink': None,
        'image_hyperlink': None,
        'comments': comments_to_dict(movie.reviews),
        'genres': genres_to_dict(movie.genres)
    }
    return movie_dict


def movies_to_dict(movies: Iterable[Movie]):
    return [movie_to_dict(movie) for movie in movies]


def comment_to_dict(comment: Review):
    comment_dict = {
        'username': comment.user.user_name,
        'movie_id': comment.movie.id,
        'comment_text': comment.review_text,
        'timestamp': comment.timestamp
    }
    return comment_dict


def comments_to_dict(comments: Iterable[Review]):
    return [comment_to_dict(comment) for comment in comments]


def genre_to_dict(new_g: Genre):
    genre_dict = {
        'name': new_g.genre_name,
        'tagged_movies': [genre.id for genre in new_g.movie_list]
    }
    return genre_dict


def genres_to_dict(genres: Iterable[Genre]):
    return [genre_to_dict(genre) for genre in genres]


# ============================================
# Functions to convert dicts to model entities
# ============================================

def dict_to_movies(dict):
    movie = Movie(dict.id, dict.year, dict.title)
    movie.description = dict.description
    movie.hyperlink = dict.hyperlink
    # Note there's no comments or tags.
    return movie
