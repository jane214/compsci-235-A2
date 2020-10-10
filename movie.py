from flask import Blueprint, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired
import movie_web_app.adapters.repository as repo

movie_blueprint = Blueprint(
    'movie_bp', __name__
)


@movie_blueprint.route('/')
def home():
    return render_template(
        'home.html',
        list_movie_url=url_for('movie_bp.list_movie'),
        find_movie_by_director_url=None,
        find_movie_by_genre_url=None,
        find_movie_by_actor=None
    )


@movie_blueprint.route('/list')
def list_movie():
    return render_template('list_movie.html',
                           list_movie_url=url_for('movie_bp.list_movie'),
                           find_movie_by_director_url=None,
                           find_movie_by_genre_url=None,
                           find_movie_by_actor=None,
                           movies=repo.repo_instance,
                           )


@movie_blueprint.route('/find', methods=['GET', 'POST'])
def find_movie_by_director():
    person = None
    form = SearchForm()

    if form.validate_on_submit():
        post_id = int(form.person_id.data)
        people_list = repo.repo_instance
        print(people_list)
        for p in people_list:
            if p.id_number == post_id:
                person = p
        return render_template('list_person.html',
                               person=person,
                               find_person_url=url_for('movie_bp.find_person'),
                               list_people_url=url_for('movie_bp.list_people')
                               )

    return render_template('find_person.html',
                           find_person_url=url_for('movie_bp.find_person'),
                           list_people_url=url_for('movie_bp.list_people'),
                           handler_url=url_for('movie_bp.find_person'),
                           form=form)


class SearchForm(FlaskForm):
    person_id = IntegerField('Person id', [DataRequired(message='Your id is required')])
    submit = SubmitField('Find')
