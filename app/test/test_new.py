import sys
import unittest
import warnings
from pathlib import Path
import pandas as pd
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.utils import create_colored_tags, \
    beautify_feedback_data, create_movie_genres, send_email_to_user

warnings.filterwarnings("ignore")

class Tests(unittest.TestCase):
    # 现有的测试用例...

    def test_beautify_feedback_data_empty(self):
        """Test case 5: Handle empty feedback data"""
        data = {}
        result = beautify_feedback_data(data)
        expected_result = {"Liked": [], "Disliked": [], "Yet to Watch": []}
        self.assertTrue(result == expected_result)

    def test_beautify_feedback_data_no_likes(self):
        """Test case 6: Handle feedback with no likes"""
        data = {'Movie 1': 'Dislike', 'Movie 2': 'Yet to watch'}
        result = beautify_feedback_data(data)
        expected_result = {"Liked": [], "Disliked": ['Movie 1'], "Yet to Watch": ['Movie 2']}
        self.assertTrue(result == expected_result)

    def test_create_colored_tags_multiple(self):
        """Test case 7: Test multiple tags with both defined and undefined genres"""
        # Define genres including a genre not in the dictionary
        genres = ['Musical', 'Drama', 'Unknown Genre']
        
        # Expected HTML output, with default color for unknown genre
        expected_result = (
            '<span style="background-color: #FF1493; color: #FFFFFF; padding: 5px; border-radius: 5px;">Musical</span> '
            '<span style="background-color: #8B008B; color: #FFFFFF; padding: 5px; border-radius: 5px;">Drama</span> '
            '<span style="background-color: #CCCCCC; color: #FFFFFF; padding: 5px; border-radius: 5px;">Unknown Genre</span>'
        )
        
        # Call function and check if output matches expected result
        result = create_colored_tags(genres)
        self.assertEqual(result, expected_result)

    def test_create_movie_genres_incomplete_data(self):
        """Test case 8: Handle incomplete genre data"""
        data = [["862", "Toy Story (1995)", "Animation|Comedy|Family", "tt0114709", " ", "/rhIRbceoE9lR4veEXuwCC2wARtG.jpg", "81"],
                ["8844", "Jumanji (1995)", None, "tt0113497", " ", "/vzmL6fP7aPKNKPRTFnZmiUfciyV.jpg", "104"]]
        movie_genre_df = pd.DataFrame(data, columns=['movieId', 'title', 'genres', 'imdb_id', 'overview', 'poster_path', 'runtime'])
        result = create_movie_genres(movie_genre_df)
        expected_result = {'Toy Story (1995)': ['Animation', 'Comedy', 'Family'], 'Jumanji (1995)': []}
        self.assertTrue(result == expected_result)

    def test_send_email_to_user_invalid_email(self):
        """Test case 9: Handle invalid email address"""
        data = {"Liked": ['Toy Story (1995)'], "Disliked": [], "Yet to Watch": []}
        with self.assertRaises(Exception):
            send_email_to_user("invalid_email", beautify_feedback_data(data))

    def test_send_email_to_user_empty_data(self):
        """Test case 10: Handle empty data for email"""
        data = {"Liked": [], "Disliked": [], "Yet to Watch": []}
        with self.assertRaises(Exception):
            send_email_to_user("valid_email@example.com", beautify_feedback_data(data))

    def test_beautify_feedback_data_invalid_status(self):
        """Test case 11: Handle invalid feedback status"""
        data = {'Movie 1': 'Unknown', 'Movie 2': 'Like'}
        result = beautify_feedback_data(data)
        expected_result = {"Liked": ['Movie 2'], "Disliked": [], "Yet to Watch": []}
        self.assertTrue(result == expected_result)

    def test_create_colored_tags_empty(self):
        """Test case 12: Handle empty tags"""
        expected_result = ''
        result = create_colored_tags([])
        self.assertTrue(result == expected_result)

    def test_create_movie_genres_missing_columns(self):
        """Test case 13: Handle missing columns in DataFrame"""
        missing_genres = []
        expected_result = ''  # Expected output for empty input
        result = create_colored_tags(missing_genres)
        self.assertEqual(result, expected_result)

    def test_send_email_to_user_missing_subject(self):
        """Test case 14: Handle missing subject in email"""
        data = {"Liked": ['Toy Story (1995)'], "Disliked": [], "Yet to Watch": []}
        with self.assertRaises(Exception):
            send_email_to_user("valid_email@example.com", beautify_feedback_data(data), subject=None)

    def test_beautify_feedback_data_repeated_movies(self):
        """Test case 15: Handle repeated movie entries"""
        data = {'Movie 1': 'Like', 'Movie 2': 'Like', 'Movie 3': 'Dislike'}
        result = beautify_feedback_data(data)
        expected_result = {"Liked": ['Movie 1', 'Movie 2'], "Disliked": ['Movie 3'], "Yet to Watch": []}
        self.assertTrue(result == expected_result)

    def test_create_movie_genres_invalid_genres(self):
        """Test case 16: Handle invalid genre formats"""
        genres = ['Action', 'InvalidGenre', 'Comedy']
        expected_result = (
            '<span style="background-color: #FF0000; color: #FFFFFF; padding: 5px; border-radius: 5px;">Action</span> '
            '<span style="background-color: #CCCCCC; color: #FFFFFF; padding: 5px; border-radius: 5px;">InvalidGenre</span> '
            '<span style="background-color: #FFB500; color: #FFFFFF; padding: 5px; border-radius: 5px;">Comedy</span>'
        )
        
        result = create_colored_tags(genres)
        
        self.assertEqual(result, expected_result)


    def test_send_email_to_user_nonexistent_email_service(self):
        """Test case 17: Handle non-existent email service"""
        data = {"Liked": ['Toy Story (1995)'], "Disliked": [], "Yet to Watch": []}
        with self.assertRaises(Exception):
            send_email_to_user("valid_email@example.com", beautify_feedback_data(data), email_service='nonexistent')

    def test_beautify_feedback_data_mixed_statuses(self):
        """Test case 18: Handle mixed feedback statuses"""
        data = {'Movie 1': 'Like', 'Movie 2': 'Dislike', 'Movie 3': 'Yet to watch', 'Movie 4': 'Like'}
        result = beautify_feedback_data(data)
        expected_result = {"Liked": ['Movie 1', 'Movie 4'], "Disliked": ['Movie 2'], "Yet to Watch": ['Movie 3']}
        self.assertTrue(result == expected_result)

    def test_create_colored_tags_special_characters(self):
        """Test case 19: Handle tags with special characters"""
        genres = ['Action', 'Romance', 'Fantasy', 'Sci-Fi', 'Unknown Genre!']
        expected_result = (
            '<span style="background-color: #FF0000; color: #FFFFFF; '
            'padding: 5px; border-radius: 5px;">Action</span> '
            '<span style="background-color: #FF69B4; color: #FFFFFF; '
            'padding: 5px; border-radius: 5px;">Romance</span> '
            '<span style="background-color: #FFA500; color: #FFFFFF; '
            'padding: 5px; border-radius: 5px;">Fantasy</span> '
            '<span style="background-color: #00CED1; color: #FFFFFF; '
            'padding: 5px; border-radius: 5px;">Sci-Fi</span> '
            '<span style="background-color: #CCCCCC; color: #FFFFFF; '
            'padding: 5px; border-radius: 5px;">Unknown Genre!</span>'
        )
        
        # Call the function to test
        result = create_colored_tags(genres)
        
        # Assert that the result matches the expected output
        self.assertEqual(result, expected_result)


    def test_create_movie_genres_empty_df(self):
        """Test case 20: Handle empty DataFrame"""
        movie_genre_df = pd.DataFrame(columns=['movieId', 'title', 'genres', 'imdb_id', 'overview', 'poster_path', 'runtime'])
        result = create_movie_genres(movie_genre_df)
        expected_result = {}
        self.assertTrue(result == expected_result)

if __name__ == "__main__":
    unittest.main()
