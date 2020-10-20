from datetime import date

from flask import Blueprint
from flask import request, render_template, redirect, url_for, session

from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField, IntegerField, StringField
from wtforms.validators import DataRequired, Length, ValidationError

import movie_web_app.adapters.repository as repo
import movie_web_app.utilities.utilities as utilities
import movie_web_app.movie.services as services

from movie_web_app.authentication.authentication import login_required

# Configure Blueprint.
from movie_web_app.domainmodel.model import Actor, Director, Genre

movies_blueprint = Blueprint(
    'movies_bp', __name__)


@movies_blueprint.route('/movies_by_date', methods=['GET'])
def movies_by_date():
    # Read query parameters.
    target_year = request.args.get('year')
    movies_to_show_comments = request.args.get('view_comments_for')

    # Fetch the first and last movies in the series.
    first_movie = services.get_first_movie(repo.repo_instance)
    last_movie = services.get_last_movie(repo.repo_instance)

    if target_year is None:
        target_year = int(first_movie['year'])
    else:
        target_year = int(target_year)

    if movies_to_show_comments is None:
        # No view-comments query parameter, so set to a non-existent movies id.
        movies_to_show_comments = -1
    else:
        # Convert movies_to_show_comments from string to int.
        movies_to_show_comments = int(movies_to_show_comments)

    # Fetch movies(s) for the target date. This call also returns the previous and next dates for moviess immediately
    # before and after the target date.
    movies, previous_year, next_year = services.get_movies_by_year(target_year, repo.repo_instance)

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if len(movies) > 0:
        # There's at least one movies for the target date.
        if previous_year is not None:
            # There are movies on a previous year, so generate URLs for the 'previous' and 'first' navigation buttons.
            prev_movie_url = url_for('movies_bp.movies_by_date', year=int(previous_year))
            first_movie_url = url_for('movies_bp.movies_by_date', year=int(first_movie['year']))

        # There are moviess on a subsequent date, so generate URLs for the 'next' and 'last' navigation buttons.
        if next_year is not None:
            next_movie_url = url_for('movies_bp.movies_by_date', year=int(next_year))
            last_movie_url = url_for('movies_bp.movies_by_date', year=int(last_movie['year']))

        # Construct urls for viewing movies comments and adding comments.
        for movie in movies:
            movie['view_comment_url'] = url_for('movies_bp.movies_by_date', year=target_year,
                                                view_comments_for=movie['id'])
            movie['add_comment_url'] = url_for('movies_bp.comment_on_movies', movie=movie['id'])
            # movie['add_to_watch_list_url'] =

        # Generate the webpage to display the moviess.
        return render_template(
            'movies/movies.html',
            title='Movies',
            movies_title=target_year,
            movies=movies,
            selected_movies=utilities.get_selected_movies(len(movies) * 2),
            genre_urls=utilities.get_genres_and_urls(),
            first_movie_url=first_movie_url,
            last_movie_url=last_movie_url,
            prev_movie_url=prev_movie_url,
            next_movie_url=next_movie_url,
            show_comments_for_movies=movies_to_show_comments
        )

    # No movies to show, so return the homepage.
    return redirect(url_for('home_bp.home'))


@movies_blueprint.route('/movies_by_genre', methods=['GET'])
def movies_by_genre():
    movies_per_page = 10

    # Read query parameters.
    genre_name = request.args.get('genre')
    cursor = request.args.get('cursor')
    movies_to_show_comments = request.args.get('view_comments_for')

    if movies_to_show_comments is None:
        # No view-comments query parameter, so set to a non-existent movies id.
        movies_to_show_comments = -1
    else:
        # Convert movies_to_show_comments from string to int.
        movies_to_show_comments = int(movies_to_show_comments)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve movies ids for movies that are classified with genre_name.
    movie_ids = services.get_movie_ids_for_genre(genre_name, repo.repo_instance)

    # Retrieve the batch of movies to display on the Web page.
    movies = services.get_movies_by_id(movie_ids[cursor:cursor + movies_per_page], repo.repo_instance)

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if cursor > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_movie_url = url_for('movies_bp.movies_by_genre', genre=genre_name, cursor=cursor - movies_per_page)
        first_movie_url = url_for('movies_bp.movies_by_genre', genre=genre_name)

    if cursor + movies_per_page < len(movie_ids):
        # There are further movies, so generate URLs for the 'next' and 'last' navigation buttons.
        next_movie_url = url_for('movies_bp.movies_by_genre', genre=genre_name, cursor=cursor + movies_per_page)

        last_cursor = movies_per_page * int(len(movie_ids) / movies_per_page)
        if len(movie_ids) % movies_per_page == 0:
            last_cursor -= movies_per_page
        last_movie_url = url_for('movies_bp.movies_by_genre', genre=genre_name, cursor=last_cursor)

    # Construct urls for viewing movies comments and adding comments.
    for movie in movies:
        movie['view_comment_url'] = url_for('movies_bp.movies_by_genre', genre=genre_name, cursor=cursor,
                                            view_comments_for=movie['id'])
        movie['add_comment_url'] = url_for('movies_bp.comment_on_movies', movie=movie['id'])
        # movie['add_to_watch_list_url']

    # Generate the webpage to display the movies.
    return render_template(
        'movies/movies.html',
        title='Movies',
        movies_title='Movies are Classified by ' + genre_name,
        movies=movies,
        selected_movies=utilities.get_selected_movies(len(movies) * 2),
        genre_urls=utilities.get_genres_and_urls(),
        first_movie_url=first_movie_url,
        last_movie_url=last_movie_url,
        prev_movie_url=prev_movie_url,
        next_movie_url=next_movie_url,
        show_comments_for_movies=movies_to_show_comments
    )


@movies_blueprint.route('/watch_list', methods=['POST'])
@login_required
def watch_list():
    username = session['username']
    movie_id = request.args.get('movie_id')
    services.add_comment(movie_id, form.comment.data, username, repo.repo_instance)

    movie = services.get_movie(movie_id, repo.repo_instance)

    return redirect(url_for('movies_bp.movies_by_date', year=int(movie['year'])))


@movies_blueprint.route('/comment', methods=['GET', 'POST'])
@login_required
def comment_on_movies():
    # Obtain the username of the currently logged in user.
    username = session['username']

    # Create form. The form maintains state, e.g. when this method is called with a HTTP GET request and populates
    # the form with an movies id, when subsequently called with a HTTP POST request, the movies id remains in the
    # form.
    form = CommentForm()

    if form.validate_on_submit():
        # Successful POST, i.e. the comment text has passed data validation.
        # Extract the movies id, representing the commented movies, from the form.
        movie_id = int(form.movie_id.data)

        # Use the service layer to store the new comment.
        services.add_comment(movie_id, form.comment.data, username, repo.repo_instance)

        # Retrieve the movies in dict form.
        movie = services.get_movie(movie_id, repo.repo_instance)

        # Cause the web browser to display the page of all movies that have the same date as the commented movies,
        # and display all comments, including the new comment.
        return redirect(url_for('movies_bp.movies_by_date', year=int(movie['year']), view_comments_for=movie_id))

    if request.method == 'GET':
        # Request is a HTTP GET to display the form.
        # Extract the movies id, representing the movies to comment, from a query parameter of the GET request.
        movie_id = int(request.args.get('movie'))

        # Store the movies id in the form.
        form.movie_id.data = movie_id
    else:
        # Request is a HTTP POST where form validation has failed.
        # Extract the movies id of the movies being commented from the form.
        movie_id = int(form.movie_id.data)

    # For a GET or an unsuccessful POST, retrieve the movies to comment in dict form, and return a Web page that allows
    # the user to enter a comment. The generated Web page includes a form object.
    movie = services.get_movie(movie_id, repo.repo_instance)
    return render_template(
        'movies/comment_on_movie.html',
        title='Edit movies',
        movie=movie,
        form=form,
        handler_url=url_for('movies_bp.comment_on_movies'),
        selected_movies=utilities.get_selected_movies(),
        genre_urls=utilities.get_genres_and_urls(),
    )


@movies_blueprint.route('/search_by_genre', methods=['GET'])
def search_by_genre():
    return render_template('movies/genre_search.html',
                           genre_urls=utilities.get_genres_and_urls(),
                           selected_movies=utilities.get_selected_movies()
                           )


@movies_blueprint.route('/movies_by_search', methods=['GET'])
def movies_by_search():
    movies_per_page = 10

    # Read query parameters.
    movies = request.args.get('movies')
    cursor = request.args.get('cursor')
    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve movies ids for movies
    movie_ids = []
    for movie in movies:
        movie_ids += movie.id

    # Retrieve the batch of movies to display on the Web page.
    movies_to_show = services.get_movies_by_id(movie_ids[cursor:cursor + movies_per_page], repo.repo_instance)

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if cursor > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_movie_url = url_for('movies_bp.movies_by_search', movies=movies, cursor=cursor - movies_per_page)
        first_movie_url = url_for('movies_bp.movies_by_search', movies=movies)

    if cursor + movies_per_page < len(movie_ids):
        # There are further movies, so generate URLs for the 'next' and 'last' navigation buttons.
        next_movie_url = url_for('movies_bp.movies_by_search', movies=movies, cursor=cursor + movies_per_page)

        last_cursor = movies_per_page * int(len(movie_ids) / movies_per_page)
        if len(movie_ids) % movies_per_page == 0:
            last_cursor -= movies_per_page
        last_movie_url = url_for('movies_bp.movies_by_search', movies=movies, cursor=last_cursor)

    return render_template(
        'movies/movies.html',
        title='Movies',
        movies_title='Search Result',
        movies=movies_to_show,
        selected_movies=utilities.get_selected_movies(len(movies) * 2),
        genre_urls=utilities.get_genres_and_urls(),
        first_movie_url=first_movie_url,
        last_movie_url=last_movie_url,
        prev_movie_url=prev_movie_url,
        next_movie_url=next_movie_url,
    )


# @movies_blueprint.route('/list_movies', methods=['GET'])
# def list_movies():
#

@movies_blueprint.route('/search_movies', methods=['GET', 'POST'])
def search_movies():
    movies = []
    form = SearchForm()
    if form.validate_on_submit():
        name = form.search_info.data
        movies = services.get_search_info(Actor(name), Genre(name), Director(name), repo.repo_instance)
        if movies is not None:
            # return redirect(url_for('movies_bp.movies_by_search', movies=movies))
            return render_template('search_result.html',
                                   movies=movies,
                                   selected_movies=utilities.get_selected_movies(),
                                   genre_urls=utilities.get_genres_and_urls()
                                   )
    return render_template('search.html',
                           search_url=url_for('movies_bp.search_movies'),
                           form=form,
                           selected_movies=utilities.get_selected_movies()
                           )


# @movies_blueprint.route('/watching_list', methods=['GET', 'POST'])
# def watching_list():
#


class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)


class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', [
        DataRequired(),
        Length(min=4, message='Your comment is too short'),
        ProfanityFree(message='Your comment must not contain profanity')])
    movie_id = HiddenField('Movie id')
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    search_info = TextAreaField('search_info', [DataRequired(message='Please give me some information')])
    submit = SubmitField('Search')
