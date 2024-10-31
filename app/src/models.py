"""
Copyright (c) 2023 Abhinav Sinha, Chandana Ray, Sam Kwiatkowski-Martin, Tanmay Pardeshi
This code is licensed under MIT license (see LICENSE for details)

@author: PopcornPicks
"""
from flask_login import UserMixin
from src import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    """
        Function to get current user
    """
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """
        User Model Table
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    reviews = db.relationship('Review', backref='user_author', lazy=True)

    def __repr__(self):
        return f" {self.first_name} {self.last_name}"

# pylint: disable=R0903
class Movie(db.Model):
    """
        Movie Table
    """
    movieId = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    runtime = db.Column(db.Integer, nullable=True)
    overview = db.Column(db.Text, nullable=True)
    genres = db.Column(db.String(500), nullable=False)
    imdb_id = db.Column(db.String(20), nullable=False)
    poster_path = db.Column(db.String(200), nullable=True)
    reviews = db.relationship('Review', backref='movie_author', lazy=True)

    def __repr__(self):
        return f"{self.movieId} - {self.title}"

# pylint: disable=R0903
class Review(db.Model):
    """
        Review Table
    """
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    review_text = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movieId = db.Column(db.Integer, db.ForeignKey('movie.movieId'), nullable=False)

    def __repr__(self):
        return f"{self.user_id} - {self.movieId}"

class ListMovie(db.Model):
    """
        List Table
    """
    list_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movieId = db.Column(db.Integer, db.ForeignKey('movie.movieId'), nullable=False)

    def __repr__(self):
        return f"{self.user_id} - {self.movieId}"
