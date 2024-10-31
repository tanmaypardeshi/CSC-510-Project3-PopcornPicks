"""
Copyright (c) 2023 Abhinav Sinha, Chandana Ray, Sam Kwiatkowski-Martin, Tanmay Pardeshi
This code is licensed under MIT license (see LICENSE for details)

@author: PopcornPicks
"""

import os
import re
import pandas as pd

app_dir = os.path.dirname(os.path.abspath(__file__))
code_dir = os.path.dirname(app_dir)
project_dir = os.path.dirname(code_dir)

def extract_year_from_title(title):
    """
    Extracts the year from a movie title string.
    """
    match = re.search(r'\((\d{4})\)', title)
    if match:
        return int(match.group(1))  # Extract the year as an integer
    return None

def recommend_for_new_user(user_rating, selected_genre=None, selected_year=None): # pylint: disable=too-many-locals
    """
    Generates a list of recommended movie titles for a new user based on their ratings.
    """
    # ratings = pd.read_csv(os.path.join(project_dir, "data", "ratings.csv"))
    movies = pd.read_csv(os.path.join(project_dir, "data", "movies.csv"))
    user = pd.DataFrame(user_rating)
    user_movie_id = movies[movies["title"].isin(user["title"])]
    user_ratings = pd.merge(user_movie_id, user)

    movies_genre_filled = movies.copy(deep=True)
    copy_of_movies = movies.copy(deep=True)

    for index, row in copy_of_movies.iterrows():
        copy_of_movies.at[index, "genres"] = row["genres"].split("|")

    for index, row in copy_of_movies.iterrows():
        for genre in row["genres"]:
            movies_genre_filled.at[index, genre] = 1

    movies_genre_filled = movies_genre_filled.fillna(0)

    user_genre = movies_genre_filled[movies_genre_filled.movieId.isin(user_ratings.movieId)]
    user_genre.drop(["movieId", "title", "genres", "imdb_id", "overview", "poster_path", "runtime"],
                     axis=1, inplace=True)
    user_profile = user_genre.T.dot(user_ratings.rating.to_numpy())

    movies_genre_filled.set_index(movies_genre_filled.movieId)
    movies_genre_filled.drop(["movieId", "title", "genres", "imdb_id", "overview", "poster_path",
                               "runtime"], axis=1, inplace=True)

    recommendations = (movies_genre_filled.dot(user_profile)) / user_profile.sum()

    join_movies_and_recommendations = movies.copy(deep=True)
    join_movies_and_recommendations["recommended"] = recommendations
    join_movies_and_recommendations.sort_values(
        by="recommended", ascending=False, inplace=True
    )
    if selected_genre:
        join_movies_and_recommendations = join_movies_and_recommendations[
            join_movies_and_recommendations["genres"].str.contains(selected_genre, case=False)
        ]

    if selected_year:
        join_movies_and_recommendations = join_movies_and_recommendations[
            join_movies_and_recommendations["title"].apply(extract_year_from_title) == selected_year
        ]
    return join_movies_and_recommendations[:9]
