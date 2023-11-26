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
    def __repr__(self):
        return f" {self.first_name} {self.last_name}"
