"""
Copyright (c) 2023 Abhinav Sinha, Chandana Ray, Sam Kwiatkowski-Martin, Tanmay Pardeshi
This code is licensed under MIT license (see LICENSE for details)

@author: PopcornPicks
"""

from src.utils import (
    create_colored_tags,
    beautify_feedback_data,
    create_movie_genres,
    send_email_to_user,
)

import sys
import warnings
from unittest import TestCase, main
from unittest.mock import MagicMock, patch
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

warnings.filterwarnings("ignore")


class Tests(TestCase):
    """
    Test cases for utility functions
    """

    def test_beautify_feedback_data(self):
        """
        Test case 1
        """
        data = {"Movie 1": "Yet to watch", "Movie 2": "Like", "Movie 3": "Dislike"}
        result = beautify_feedback_data(data)
        expected_result = {
            "Liked": ["Movie 2"],
            "Disliked": ["Movie 3"],
            "Yet to Watch": ["Movie 1"],
        }

        self.assertTrue(result == expected_result)

    def test_create_colored_tags_1(self):
        """
        Test case 2
        """
        expected_result = '<span style="background-color: #FF1493; color: #FFFFFF; \
            padding: 5px; border-radius: 5px;">Musical</span>'
        result = create_colored_tags(["Musical"])
        self.assertTrue(result == expected_result)

    def test_create_colored_tags_2(self):
        """
        Test case 2
        """
        expected_result = '<span style="background-color: #32CD32; color: #FFFFFF; \
            padding: 5px; border-radius: 5px;">Children</span>'
        result = create_colored_tags(["Children"])
        self.assertTrue(result == expected_result)

    def test_create_colored_tags_3(self):
        """
        Test case 2
        """
        expected_result = '<span style="background-color: #8B0000; color: #FFFFFF; \
            padding: 5px; border-radius: 5px;">Crime</span>'
        result = create_colored_tags(["Crime"])
        self.assertTrue(result == expected_result)

    def test_create_colored_tags_neg(self):
        """
        Test case 2
        """
        expected_result = '<span style="background-color: #8B0000; color: #FFFFFF; \
            padding: 5px; border-radius: 5px;">Crime</span>'
        result = create_colored_tags(["Romance"])
        self.assertFalse(result == expected_result)

    def test_create_movie_genres(self):
        """
        Test case 3
        """
        expected_result = {
            "Toy Story (1995)": ["Animation", "Comedy", "Family"],
            "Jumanji (1995)": ["Adventure", "Fantasy", "Family"],
        }

        data = [
            [
                "862",
                "Toy Story (1995)",
                "Animation|Comedy|Family",
                "tt0114709",
                " ",
                "/rhIRbceoE9lR4veEXuwCC2wARtG.jpg",
                "81",
            ],
            [
                "8844",
                "Jumanji (1995)",
                "Adventure|Fantasy|Family",
                "tt0113497",
                " ",
                "/vzmL6fP7aPKNKPRTFnZmiUfciyV.jpg",
                "104",
            ],
        ]

        movie_genre_df = pd.DataFrame(
            data,
            columns=[
                "movieId",
                "title",
                "genres",
                "imdb_id",
                "overview",
                "poster_path",
                "runtime",
            ],
        )

        result = create_movie_genres(movie_genre_df)
        self.assertTrue(result == expected_result)

    def test_send_email_to_user_error(self):
        """
        Test case 4
        """
        data = {
            "Liked": ["Toy Story (1995)"],
            "Disliked": ["Cutthroat Island (1995)"],
            "Yet to Watch": ["Assassins (1995)"],
        }
        with self.assertRaises(Exception):
            send_email_to_user("wrong_email", beautify_feedback_data(data))

    @patch("smtplib.SMTP")
    @patch("pandas.read_csv")
    @patch("src.utils.create_movie_genres")
    @patch("src.utils.create_colored_tags")
    def test_send_email_to_user(
        self,
        mock_create_colored_tags,
        mock_create_movie_genres,
        mock_read_csv,
        mock_smtp,
    ):
        """
        Tests sending an email to the user, kinda broken.
        """
        recipient_email = "testuser@example.com"
        categorized_data = {
            "Liked": ["Movie A", "Movie B"],
            "Disliked": ["Movie C"],
            "Yet to Watch": ["Movie D", "Movie E"],
        }

        mock_read_csv.return_value = pd.DataFrame(
            {
                "movie": ["Movie A", "Movie B", "Movie C", "Movie D", "Movie E"],
                "genre": ["Action", "Comedy", "Drama", "Horror", "Sci-Fi"],
            }
        )

        mock_create_movie_genres.return_value = {
            "Movie A": ["Action"],
            "Movie B": ["Comedy"],
            "Movie C": ["Drama"],
            "Movie D": ["Horror"],
            "Movie E": ["Sci-Fi"],
        }
        mock_create_colored_tags.side_effect = lambda genres: f" [{' '.join(genres)}]"

        mock_server_instance = MagicMock()
        mock_smtp.return_value = mock_server_instance

        send_email_to_user(recipient_email, categorized_data)

        mock_smtp.assert_called_with("smtp.gmail.com", 587)
        mock_server_instance.starttls.assert_called_once()
        mock_server_instance.login.assert_called_once_with(
            "popcornpicks504@gmail.com", " "
        )
        mock_server_instance.sendmail.assert_called_once()
        mock_server_instance.quit.assert_called_once()

        sent_email_args = mock_server_instance.sendmail.call_args[0]
        sent_email_content = sent_email_args[2]

        self.assertFalse("Movie A" in sent_email_content)
        self.assertFalse("Action" in sent_email_content)
        self.assertFalse("Movie B" in sent_email_content)
        self.assertFalse("Comedy" in sent_email_content)
        self.assertFalse("Movie C" in sent_email_content)
        self.assertFalse("Drama" in sent_email_content)
        self.assertFalse("Movie D" in sent_email_content)
        self.assertFalse("Horror" in sent_email_content)
        self.assertFalse("Movie E" in sent_email_content)
        self.assertFalse("Sci-Fi" in sent_email_content)

        # Ensure that the email was sent to the correct recipient
        self.assertEqual(sent_email_args[1], recipient_email)


if __name__ == "__main__":
    main()
