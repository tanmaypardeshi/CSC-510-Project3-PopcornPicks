"""
Copyright (c) 2023 Aditya Pai, Ananya Mantravadi, Rishi Singhal, Samarth Shetty
This code is licensed under MIT license (see LICENSE for details)

@author: PopcornPicks
"""

import json
import sys

from flask import Flask, jsonify, render_template, request, session, redirect
from flask_cors import CORS
from search import Search
from utils import beautify_feedback_data, send_email_to_user

sys.path.append("../../")
#pylint: disable=wrong-import-position
from src.prediction_scripts.item_based import recommend_for_new_user
#pylint: enable=wrong-import-position
import db

app = Flask(__name__)
app.secret_key = "secret key"

cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Connect to the database
db.connect()
# Initialize the database for users
db.mutation_query('''
        CREATE TABLE IF NOT EXISTS users (
            email    varchar(500),
            password    varchar(500)
        )
    ''')

def get_user():
    """
    Returns the user's email if a user is logged in, otherwise returns none
    """
    ret = 'None'
    if 'email' in session:
        # An email is in the session
        ret = session['email']
    return ret

@app.route("/")
def landing_page():
    """
    Renders the landing page with the user.
    """
    return render_template("landing_page.html", user=get_user())

@app.route("/login")
def login_page():
    """
    Renders the login page.
    """
    return render_template("login.html", user=get_user())

@app.route("/signup")
def signup_page():
    """
    Renders the signup page.
    """
    return render_template("signup.html", user=get_user())

@app.route("/search_page")
def search_page():
    """
    Renders the search page.
    """
    return render_template("search_page.html", user=get_user())

@app.route('/processSignup', methods = ["POST","GET"])
def processSignup():
    """
    Queries the database to see if the user already exists. If so it lets the javascript know
    If not, the new user is added to the database
    """
    ret = {}
    # Below is how we create a dictionary of the data sent from the input form
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    # query to see if user in the database already
    user_query = f"SELECT * FROM users where email=?"
    result = db.select_query(user_query, (form_fields["email"],))
    result = result.fetchone() # get the first row
    if result is None:
        # if email is not in the database then we add it
        add_user_query = f"INSERT INTO users (email, password) VALUES (?,?)"
        db.mutation_query(add_user_query, (form_fields["email"], form_fields["password"]))
        ret["success"] = 1  # send a success indicator back to the javascript side
    # If user is in database, then send a failure indicator
    else:
        ret["success"] = 0

    return ret

@app.route('/processLogin', methods = ["POST","GET"])
def processLogin():
    """
    Checks to see if the username name and password are valid
    If so, the user is logged in via adding their email to the session data
    Otherwise the javascript is told there was a mistake.
    """
    ret = {}
    # Below is how we create a dictionary of the data sent from the input form
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    # query to see if user in the database
    user_query = f"SELECT * FROM users where email=? and password=?"
    result = db.select_query(user_query, (form_fields["email"], form_fields["password"]))
    result = result.fetchone() # get the first row
    if result is None:
        # if email and password is not in the database then we add it then send failure indicator
        ret["success"] = 0

    # If email and password is in the database we log the user in
    else:
        session['email'] = form_fields["email"] # add the email to the users session
        ret["success"] = 1
    return ret

@app.route('/logout')
def logout():
    """
    Logs the current user out by poping their email from current session
    """
    session.pop('email', default=None)
    return redirect('/')

@app.route("/predict", methods=["POST"])
def predict():
    """
    Predicts movie recommendations based on user ratings.
    """
    data = json.loads(request.data)
    data1 = data["movie_list"]
    training_data = []
    for movie in data1:
        movie_with_rating = {"title": movie, "rating": 5.0}
        if movie_with_rating not in training_data:
            training_data.append(movie_with_rating)
    recommendations, genres, imdb_id = recommend_for_new_user(training_data)
    recommendations, genres, imdb_id = recommendations[:10], genres[:10], imdb_id[:10]
    resp = {"recommendations": recommendations, "genres": genres, "imdb_id":imdb_id}
    return resp


@app.route("/search", methods=["POST"])
def search():
    """
    Handles movie search requests.
    """
    term = request.form["q"]
    finder = Search()
    filtered_dict = finder.results_top_ten(term)
    resp = jsonify(filtered_dict)
    resp.status_code = 200
    return resp


@app.route("/feedback", methods=["POST"])
def feedback():
    """
    Handles user feedback submission and mails the results.
    """
    data = json.loads(request.data)
    return data


@app.route("/sendMail", methods=["POST"])
def send_mail():
    """
    Handles user feedback submission and mails the results.
    """
    data = json.loads(request.data)
    user_email = data['email']
    send_email_to_user(user_email, beautify_feedback_data(data))
    return data


@app.route("/success")
def success():
    """
    Renders the success page.
    """
    return render_template("success.html", user=get_user())


if __name__ == "__main__":
    app.run(port=5000)
