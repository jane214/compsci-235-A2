from flask import Flask
from movie_web_app.adapters.Movie_repo import MovieRepo, populate
from movie_web_app.datafilereaders.movie_file_csv_reader import MovieFileCSVReader
import movie_web_app.adapters.repository as repo


def create_app(test_config=None):
    # Create the Flask app object.
    app = Flask(__name__)

    # Configure the app from configuration-file settings.
    app.config.from_object('config.Config')
    data_path = "C:/Users/zhong/Desktop/compsci-235-A2/movie_web_app/datafilereaders"

    if test_config is not None:
        # Load test configuration, and overrride any configuration settings.
        app.config.from_mapping(test_config)
        data_path = app.config['TEST_DATA_PATH']

    with app.app_context():
        # Register blueprints.
        from .home import home
        app.register_blueprint(home.home_blueprint)

        from .movie import movie_page
        app.register_blueprint(movie_page.movies_blueprint)

        from .authentication import authentication
        app.register_blueprint(authentication.authentication_blueprint)

        from .utilities import utilities
        app.register_blueprint(utilities.utilities_blueprint)


    # #filename = 'movie_web_app/datafilereaders/Data1000Movies.csv'
    # movie_file = MovieFileCSVReader(filename)
    # movie_file.read_csv_file()
    # repo.repo_instance = repo.MovieRepo(movie_file.dataset_of_movies)
    # repo._actors = movie_file.dataset_of_actors
    # repo._director = movie_file.dataset_of_directors
    # repo._genres = movie_file.dataset_of_genres
    # for movie in repo.repo_instance:
    #     print(movie, movie.id)

    repo.repo_instance = MovieRepo()
    populate(data_path, repo.repo_instance)
    # for movie in repo.repo_instance:
    #     print(movie)
    #
    # print("first_movie", repo.repo_instance.get_first_movie())
    return app
