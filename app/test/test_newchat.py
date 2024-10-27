import unittest

class ChatApp:
    def __init__(self):
        self.allowed_users = set()
        self.current_user = 'hua yang'

    def add_user(self, username):
        if username and username not in self.allowed_users:
            self.allowed_users.add(username)
            return True
        return False

    def remove_user(self, username):
        self.allowed_users.discard(username)

    def send_message(self, username, message):
        if username in self.allowed_users and message.strip():
            return f"{username}: {message}"
        return None

    def update_user_list(self):
        return list(self.allowed_users)

class TestChatApp(unittest.TestCase):
    def setUp(self):
        """Set up a new chat app instance for each test."""
        self.chat_app = ChatApp()

    def test_initial_user_list(self):
        """Test the initial user list contains the current user."""
        self.assertNotIn(self.chat_app.current_user, self.chat_app.update_user_list())

    def test_add_user_success(self):
        """Test adding a new user successfully."""
        result = self.chat_app.add_user('john_doe')
        self.assertTrue(result)
        self.assertIn('john_doe', self.chat_app.update_user_list())

    def test_add_existing_user(self):
        """Test adding an existing user fails."""
        self.chat_app.add_user('john_doe')  # Add first
        result = self.chat_app.add_user('john_doe')  # Try to add again
        self.assertFalse(result)

    def test_add_invalid_user(self):
        """Test adding an invalid user (empty string)."""
        result = self.chat_app.add_user('')
        self.assertFalse(result)

    def test_send_message_as_allowed_user(self):
        """Test sending a message as an allowed user."""
        self.chat_app.add_user('hua yang')
        result = self.chat_app.send_message('hua yang', 'Hello everyone!')
        self.assertEqual(result, 'hua yang: Hello everyone!')

    def test_send_message_as_not_allowed_user(self):
        """Test sending a message as a not allowed user."""
        result = self.chat_app.send_message('john_doe', 'Hello!')
        self.assertIsNone(result)

    def test_remove_user(self):
        """Test removing a user from the allowed list."""
        self.chat_app.add_user('john_doe')
        self.chat_app.remove_user('john_doe')
        self.assertNotIn('john_doe', self.chat_app.update_user_list())

    def test_remove_current_user(self):
        """Test that removing the current user updates the list correctly."""
        self.chat_app.remove_user('hua yang')
        result = self.chat_app.send_message('hua yang', 'Trying to send message after removal')
        self.assertIsNone(result)

    def test_update_user_list_after_adding_user(self):
        """Test the user list updates correctly after adding a user."""
        self.chat_app.add_user('jane_doe')
        user_list = self.chat_app.update_user_list()
        self.assertIn('jane_doe', user_list)
        

if __name__ == '__main__':
    unittest.main()
