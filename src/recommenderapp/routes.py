"""
Copyright (c) 2023 Aditya Pai, Ananya Mantravadi, Rishi Singhal, Samarth Shetty
This code is licensed under MIT license (see LICENSE for details)

@author: PopcornPicks
"""

import json
import sys

from flask import render_template, url_for, flash, redirect, request, session
from flask_login import login_user, current_user, logout_user, login_required
from recommenderapp import app, db, bcrypt
from recommenderapp.search import Search
from recommenderapp.utils import beautify_feedback_data, send_email_to_user
from recommenderapp.item_based import recommend_for_new_user
from recommenderapp.models import User

"""
    Renders the landing page with the user.
"""
@app.route("/", methods={"GET"})
@app.route("/home", methods={"GET"})
def landing_page():
    if current_user.is_authenticated:
        return redirect(url_for('search_page'))
    return render_template("landing_page.html")

"""
    Login Page Flow 
"""
@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        # If user has already logged in earlier and has an active session
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        # If user has not logged in and a login request is sent by the user
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(username=username).first()
            # Successful Login
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                print("Logged in")
                return redirect(url_for('search_page'))
            # Invalid Credentials
            show_message = True
            message = "Invalid Credentials! Try again!"
            print(message)
            return render_template("login.html", message=message, show_message=show_message)
        # When the login page is hit
        print("Hit")
        return render_template("login.html")
    except Exception as e:
        print(f"Error is {e}")
        return render_template('login.html', message=e, show_message=True)


"""
    Signup Page Flow
"""
@app.route("/signup", methods=["GET", "POST"])
def signup():
    username = ""
    try:
        # If user has already logged in earlier and has an active session
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        # If user has not logged in and a signup request is sent by the user
        if request.method == "POST":
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            hashed_password = bcrypt.generate_password_hash(password)
            user = User(username=username, email=email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        # For GET method
        return render_template('signup.html')
    # If user already exists
    except Exception as e:
        print(f"Error is {e}")
        message = f"Username {username} already exists!"
        return render_template('signup.html', message=message, show_message=True)

@app.route("/search_page")
def search_page():
    """
    Renders the search page.
    """
    return render_template("search_page.html", user=current_user)

@app.route('/logout')
def logout():
    logout_user()
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
    return render_template("success.html", user=current_user)


if __name__ == "__main__":
    app.run(port=5000)
