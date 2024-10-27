import unittest

class ChatSystem:
    def __init__(self, current_user):
        self.allowed_users = set()
        self.current_user = current_user
        if current_user:
            self.allowed_users.add(current_user)
        self.messages = []  # List of (username, message) tuples

    # Add a message if the user is allowed
    def submit_message(self, username, message):
        if username in self.allowed_users:
            self.messages.append((username, message))
            return True  # Message added successfully
        return False  # User not allowed

    # Add a new user if not already added
    def add_user(self, username):
        if username and username not in self.allowed_users:
            self.allowed_users.add(username)
            return True  # User added successfully
        return False  # User already exists or invalid input

    # Remove a user
    def remove_user(self, username):
        if username in self.allowed_users:
            self.allowed_users.remove(username)
            return True  # User removed successfully
        return False  # User not found

    # Get the current list of allowed users
    def get_user_list(self):
        return list(self.allowed_users)

    # Get the list of messages
    def get_message_list(self):
        return self.messages


class TestChatSystem(unittest.TestCase):

    def setUp(self):
        # Initialize with a default current user
        self.chat = ChatSystem('Alice')
    
    # Test that the current user is not empty
    def test_initial_user_not_empty(self):
        self.assertTrue(self.chat.current_user)

    # Test that the current user is added initially
    def test_initial_user(self):
        self.assertIn('Alice', self.chat.get_user_list())

    # Test adding a new user
    def test_add_user_success(self):
        result = self.chat.add_user('Bob')
        self.assertTrue(result)
        self.assertIn('Bob', self.chat.get_user_list())

    # Test adding the same user again
    def test_add_existing_user(self):
        self.chat.add_user('Bob')
        result = self.chat.add_user('Bob')
        self.assertFalse(result)

    # Test adding a user with invalid input (empty username)
    def test_add_user_invalid_input(self):
        result = self.chat.add_user('')
        self.assertFalse(result)

    # Test removing a user
    def test_remove_user_success(self):
        self.chat.add_user('Bob')
        result = self.chat.remove_user('Bob')
        self.assertTrue(result)
        self.assertNotIn('Bob', self.chat.get_user_list())

    # Test removing a non-existent user
    def test_remove_non_existent_user(self):
        result = self.chat.remove_user('NonExistent')
        self.assertFalse(result)

    # Test sending a message by the current user
    def test_submit_message_success(self):
        result = self.chat.submit_message('Alice', 'Hello, world!')
        self.assertTrue(result)
        self.assertIn(('Alice', 'Hello, world!'), self.chat.get_message_list())

    # Test sending a message by an unauthorized user
    def test_submit_message_unauthorized_user(self):
        result = self.chat.submit_message('Charlie', 'Hey!')
        self.assertFalse(result)

    # Test submitting an empty message
    def test_submit_empty_message(self):
        result = self.chat.submit_message('Alice', '')
        self.assertTrue(result)
        self.assertIn(('Alice', ''), self.chat.get_message_list())

    # Test message list after multiple submissions
    def test_multiple_message_submission(self):
        self.chat.submit_message('Alice', 'First message')
        self.chat.submit_message('Alice', 'Second message')
        self.assertEqual(self.chat.get_message_list(), [('Alice', 'First message'), ('Alice', 'Second message')])

    # Test removing current user and adding back
    def test_remove_and_readd_current_user(self):
        self.chat.remove_user('Alice')
        self.assertNotIn('Alice', self.chat.get_user_list())
        self.chat.add_user('Alice')
        self.assertIn('Alice', self.chat.get_user_list())

    # Test sending message after current user is removed
    def test_message_submission_after_removal(self):
        self.chat.remove_user('Alice')
        result = self.chat.submit_message('Alice', 'Still here!')
        self.assertFalse(result)

    # Test adding multiple users and checking user list
    def test_add_multiple_users(self):
        self.chat.add_user('Bob')
        self.chat.add_user('Charlie')
        self.assertListEqual(sorted(self.chat.get_user_list()), sorted(['Alice', 'Bob', 'Charlie']))

    # Test removing all users
    def test_remove_all_users(self):
        self.chat.add_user('Bob')
        self.chat.remove_user('Alice')
        self.chat.remove_user('Bob')
        self.assertEqual(self.chat.get_user_list(), [])

    # Test adding and removing a user repeatedly
    def test_add_remove_user_repeatedly(self):
        self.chat.add_user('Bob')
        self.chat.remove_user('Bob')
        self.assertNotIn('Bob', self.chat.get_user_list())
        self.chat.add_user('Bob')
        self.assertIn('Bob', self.chat.get_user_list())

    # Test message list with no messages
    def test_empty_message_list(self):
        self.assertEqual(self.chat.get_message_list(), [])

    # Test message list after a user is removed
    def test_message_list_after_user_removal(self):
        self.chat.add_user('Bob')
        self.chat.submit_message('Bob', 'Hi!')
        self.chat.remove_user('Bob')
        self.assertIn(('Bob', 'Hi!'), self.chat.get_message_list())

    # Test sending message with long text
    def test_submit_long_message(self):
        long_message = 'A' * 1000
        result = self.chat.submit_message('Alice', long_message)
        self.assertTrue(result)
        self.assertIn(('Alice', long_message), self.chat.get_message_list())

    # Test removing current user and preventing message submission
    def test_remove_current_user_and_prevent_message(self):
        self.chat.remove_user('Alice')
        result = self.chat.submit_message('Alice', 'Should not send')
        self.assertFalse(result)
    
    

if __name__ == '__main__':
    unittest.main()
