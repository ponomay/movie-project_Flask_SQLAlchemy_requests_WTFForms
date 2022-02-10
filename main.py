from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FloatField, HiddenField
from wtforms.validators import DataRequired
import requests
from sqlalchemy import desc
import json

API_key = "3e1a4cd8aacad6cc99577ff5f2588892"
end_point = "https://api.themoviedb.org/3/search/movie"



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float(250), nullable=False)
    ranking = db.Column(db.Float(250), nullable=False)
    review = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(), nullable=False)

    def __init__(self, title, year, description, rating, ranking, review, img_url):
        self.title = title
        self.year = year
        self.rating = rating
        self.description = description
        self.ranking = ranking
        self.review = review
        self.img_url = img_url

class RateMovieForm(FlaskForm):
    rating = FloatField('My rating', validators=[DataRequired()])
    review = TextAreaField('My review', validators=[DataRequired()])
    submit = SubmitField("Update")
    movie_id = HiddenField()


class AddMovie(FlaskForm):
    title = StringField('Add Title', validators=[DataRequired()])
    submit = SubmitField("Send")

db.create_all()
# db.session.add(new_movie)
# db.session.commit()



@app.route("/")
def home():
    return render_template("index.html", movies=Movie.query.order_by(desc(Movie.rating)).all())


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = AddMovie()
    if form.validate_on_submit():
        film_to_seek = form.title.data
        parameters = {
            "query": film_to_seek,
            "api_key": API_key,
        }
        response_full = requests.get(url=end_point, params=parameters).json()
        response = response_full['results']
        for film in response:
            print(film)
            return render_template('select.html', response=response)
    return render_template("add.html", form=form)

@app.route("/search/<film_id>", methods=["GET", "POST"])
def search(film_id):
    film_id_int = int(film_id)
    end_point2 = f"https://api.themoviedb.org/3/movie/{film_id_int}"
    parameters = {
        "api_key": API_key,
    }
    response = requests.get(url=end_point2, params=parameters).json()
    print(response)
    new_movie = Movie(
        title=response['original_title'],
        year=response['release_date'],
        description=response['overview'],
        ranking=10,
        rating=10,
        review="",
        img_url=f"https://image.tmdb.org/t/p/w500{response['poster_path']}")
    db.session.add(new_movie)
    db.session.commit()
    print(new_movie.id)
    return redirect(url_for('edit', movie_id=new_movie.id))


@app.route("/edit/<movie_id>", methods=["GET", "POST"])
def edit(movie_id):
    form = RateMovieForm()
    form.movie_id = movie_id
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = form.rating.data
        movie_to_update.review = form.review.data
        db.session.commit()
        ##add to db
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, movie=movie)

@app.route("/delete/<movie_id>", methods=["GET", "POST"])
def delete(movie_id):
    movie = Movie.query.get(movie_id)
    print(movie.title)
    Movie.query.filter_by(id=movie_id).delete()
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
