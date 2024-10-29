"""
Copyright (c) 2023 Abhinav Sinha, Chandana Ray, Sam Kwiatkowski-Martin, Tanmay Pardeshi
This code is licensed under MIT license (see LICENSE for details)

@author: PopcornPicks
"""

import json
import os
import requests

from flask import render_template, url_for, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import emit
from dotenv import load_dotenv
import pandas as pd
from src import app, db, bcrypt, socket
from src.search import Search
from src.item_based import recommend_for_new_user
from src.models import User, Movie, Review, ListMovie

app_dir = os.path.dirname(os.path.abspath(__file__))
code_dir = os.path.dirname(app_dir)
project_dir = os.path.dirname(code_dir)

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

@app.route("/", methods={"GET"})
@app.route("/home", methods={"GET"})
def landing_page():
    """
        Renders the landing page with the user.
    """
    if current_user.is_authenticated:
        return redirect(url_for('search_page'))
    return render_template("landing_page.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
        Signup Page Flow
    """
    username = ""
    try:
        # If user has already logged in earlier and has an active session
        if current_user.is_authenticated:
            return redirect(url_for('search_page'))
        # If user has not logged in and a signup request is sent by the user
        if request.method == "POST":
            username = request.form['username']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form['password']
            hashed_password = bcrypt.generate_password_hash(password)
            user = User(username=username, email=email, first_name=first_name,
                        last_name=last_name, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('search_page'))
        # For GET method
        return render_template('signup.html')
    # If user already exists
    #pylint: disable=broad-except
    except Exception as e:
        print(f"Error is {e}")
        message = f"Username {username} already exists!"
        return render_template('signup.html', message=message, show_message=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    """
        Login Page Flow
    """
    try:
        # If user has already logged in earlier and has an active session
        if current_user.is_authenticated:
            return redirect(url_for('search_page'))
        # If user has not logged in and a login request is sent by the user
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(username=username).first()
            # Successful Login
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('search_page'))
            # Invalid Credentials
            show_message = True
            message = "Invalid Credentials! Try again!"
            return render_template("login.html", message=message, show_message=show_message)
        # When the login page is hit
        return render_template("login.html")
    #pylint: disable=broad-except
    except Exception as e:
        print(f"Error is {e}")
        return render_template('login.html', message=e, show_message=True)

@app.route('/logout')
def logout():
    """
        Logout Function
    """
    logout_user()
    return redirect('/')

@app.route("/profile_page", methods=["GET"])
@login_required
def profile_page():
    """
        Profile Page
    """
    reviews_objects = Review.query.filter_by(user_id=current_user.id).all()
    reviews = []
    for review in reviews_objects:
        movie_object = Movie.query.filter_by(movieId=review.movieId).first()
        obj = {
            "title" : movie_object.title,
            "runtime" : movie_object.runtime,
            "overview" : movie_object.overview,
            "genres" : movie_object.genres,
            "imdb_id" : movie_object.imdb_id,
            "review_text" : review.review_text,
            "score" : review.score
        }
        reviews.append(obj)
    return render_template("profile.html", user=current_user, reviews=reviews, search=False)

@app.route("/userlist_page", methods=["GET"])
@login_required
def userlist_page():
    """
        User List Page
    """
    user_objects = User.query.all()
    movies = pd.read_csv(os.path.join(project_dir, "data", "movies.csv"))
    users_list = []
    for users in user_objects:
        obj1 = {
            "username": users.username
        }
        list_objects = ListMovie.query.filter_by(user_id = users.id)
        movies_list = []
        for obj in list_objects:
            list_movies = movies[movies['movieId'] == obj.movieId]
            list_movies = list_movies.iloc[0]
            obj2 = {
                "title": list_movies['title'],
                "runtime": list_movies['runtime'],
                "overview": list_movies['overview'],
                "genres": list_movies['genres'],
                "imdb_id": list_movies['imdb_id'],
                "movieId": list_movies['movieId']
            }
            movies_list.append(obj2)
        obj1["movies_list"] = movies_list
        users_list.append(obj1)
    return render_template(
                "userlist.html", user=current_user, search=False, users_list = users_list
            )

@app.route("/search_page", methods=["GET"])
@login_required
def search_page():
    """
        Search Page
    """
    if current_user.is_authenticated:
        return render_template("search.html", user=current_user, search=True)
    return redirect(url_for('landing_page'))

@app.route("/predict", methods=["POST"])
def predict():
    """
    Predicts movie recommendations based on user ratings.
    """
    data = json.loads(request.data)
    data1 = data["movie_list"]
    selected_genre = data.get("genre")
    release_year = data.get("year")
    training_data = []
    for movie in data1:
        movie = movie.replace("Delete", "")
        movie_with_rating = {"title": movie, "rating": 5.0}
        if movie_with_rating not in training_data:
            training_data.append(movie_with_rating)
    user_reviews = Review.query.filter_by(user_id=current_user.id).all()
    for review in user_reviews:
        movie = Movie.query.filter_by(movieId=review.movieId).first()
        movie_with_rating = {"title": movie.title, "rating": review.score}
        if movie_with_rating not in training_data:
            training_data.append(movie_with_rating)
    data = recommend_for_new_user(training_data, selected_genre, release_year)
    data = data.to_json(orient="records")
    return jsonify(data)

@app.route("/displaylist", methods=["POST"])
def displaylist():
    """
    Predicts movie recommendations based on user ratings.
    """
    data = json.loads(request.data)
    user_object = User.query.filter_by(username=current_user.username).first()
    userid = user_object.id
    data1 = data["movie_list"]
    movies = pd.read_csv(os.path.join(project_dir, "data", "movies.csv"))
    training_data = []
    for movie in data1:
        movie = movie.replace("Delete", "")
        movie_with_rating = {"title": movie}
        if movie_with_rating not in training_data:
            training_data.append(movie_with_rating)
    user = pd.DataFrame(training_data)
    data = movies[movies["title"].isin(user["title"])]
    movie_ids = data["movieId"].tolist()
    for movie_id in movie_ids:
        movie_list = ListMovie(
            user_id = userid,
            movieId = movie_id
        )
        db.session.add(movie_list)
        db.session.commit()
    data = data.to_json(orient="records")
    return jsonify(data)

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

@app.route("/chat", methods=["GET"])
def chat_page():
    """
        Renders chat room page
    """
    if current_user.is_authenticated:
        return render_template("movie_chat.html", user=current_user)
    return redirect(url_for('landing_page'))

@socket.on('connections')
def show_connection(data):
    """
        Prints out if the connection to the chat page is successful
    """
    print('received message: ' + data)

@socket.on('message')
def broadcast_message(data):
    """
        Distributes messages sent to the server to all clients in real time
    """
    emit('message', {'username': data['username'], 'msg': data['msg']}, broadcast=True)

@app.route("/getPosterURL", methods=["GET"])
def get_poster_url():
    """
    Retrieve the poster URL for the recommended movie based on IMDb ID.
    return: JSON response containing the poster URL.
    """
    imdb_id = request.args.get("imdbID")
    poster_url = fetch_poster_url(imdb_id)
    return jsonify({"posterURL": poster_url})

def fetch_poster_url(imdb_id):
    """
    Fetch the poster URL for a movie from The Movie Database (TMDB) API.
    """
    timeout = 100
    url = f"https://api.themoviedb.org/3/find/{imdb_id}?"\
    f"api_key={TMDB_API_KEY}&external_source=imdb_id"
    response = requests.get(url, timeout=timeout)
    data = response.json()
    # Check if movie results are present and have a poster path
    if "movie_results" in data and data["movie_results"]:
        poster_path = data["movie_results"][0].get("poster_path")
        return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
    return None

@app.route("/postReview", methods=["POST"])
@login_required
def post_review():
    """
        API for the user to submit a review
    """
    # Check if the movie already exists in the database.
    # If it exists, fetch the movie ID and save the review
    # If it does not, save the movie details and save the review

    data = json.loads(request.data)
    user_object = User.query.filter_by(username=current_user.username).first()
    user_id = user_object.id
    review_text = data['review_text']
    score = data['score']
    movie_id = data["movieId"]
    movie_object = Movie.query.filter_by(movieId=movie_id).first()
    if movie_object is None:
        # Create a new movie object
        movie = Movie(
            movieId = movie_id,
            title = data['title'],
            runtime = data['runtime'],
            overview = data['overview'],
            genres = data['genres'],
            imdb_id = data['imdb_id'],
            poster_path = data['poster_path']
        )
        db.session.add(movie)
        db.session.commit()
    review = Review(
        review_text = review_text,
        score=score,
        movieId = movie_id,
        user_id = user_id
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({"success": "success"})

@app.route("/movies", methods=["GET"])
@login_required
def movie_page():
    """
        Get movies and their reviews from CSV using pandas
    """
    movie_id = request.args.get('movie_id')  # Get the movie ID from the query parameters
    movie_id = int(movie_id)

    # Load the CSV file into a DataFrame
    movies_df = pd.read_csv(os.path.join(project_dir, "data", "movies.csv"))

    # Find the movie details by filtering the DataFrame
    movie_details = movies_df[movies_df['movieId'] == movie_id]

    if movie_details.empty:
        print("No movie found with the given movie_id")  # Debugging statement
        return "Movie not found", 404  # Return an error message if the movie doesn't exist

    movie_info = movie_details.iloc[0]  # Get the first matching movie
    reviews = []

    # Fetch reviews based on the movieId from the database
    reviews_objects = Review.query.filter_by(movieId=int(movie_info['movieId'])).all()
    for review_object in reviews_objects:
        user = User.query.filter_by(id=review_object.user_id).first()
        obj2 = {
            "username": user.username,
            "name": f"{user.first_name} {user.last_name}",
            "review_text": review_object.review_text
        }
        reviews.append(obj2)

    movie_info_dict = {
        "title": movie_info['title'],
        "runtime": movie_info['runtime'],
        "overview": movie_info['overview'],
        "genres": movie_info['genres'],
        "imdb_id": movie_info['imdb_id'],
        "reviews": reviews
    }

    return render_template("movie.html", movies=[movie_info_dict],
                           user=current_user)  # Return a list with one movie object


@app.route('/new_movies', methods=["GET"])
@login_required
def new_movies():
    """
        API to fetch new movies
    """
    # Replace YOUR_TMDB_API_KEY with your actual TMDb API key
    tmdb_api_key = TMDB_API_KEY
    endpoint = 'https://api.themoviedb.org/3/movie/upcoming'

    # Set up parameters for the request
    params = {
        'api_key': tmdb_api_key,
        'language': 'en-US',  # You can adjust the language as needed
        'page': 1  # You may want to paginate the results if there are many
    }
    try:
    # Make the request to TMDb API
        response = requests.get(endpoint, params=params, timeout=10)
    except (requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException
            ) as e:
        return render_template('new_movies.html', show_message=True,
                           message=e)
    if response.status_code == 200:
        # Parse the JSON response
        movie_data = response.json().get('results', [])

        return render_template('new_movies.html', movies=movie_data, user=current_user)
    return render_template('new_movies.html', show_message=True,
                           message='Error fetching movie data')

@app.route("/list", methods=["GET"])
def list_page():
    """
        Renders chat room page
    """
    if current_user.is_authenticated:
        return render_template("list.html", user=current_user)
    return redirect(url_for('landing_page'))
