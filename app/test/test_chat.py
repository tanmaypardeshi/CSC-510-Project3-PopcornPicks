import unittest
from src import app, socket

class MyTestCase(unittest.TestCase):

    def setUp(self):
        """
        Sets up the two test clients: basic and socket
        """
        self.basic_test_client = app.test_client()  # makes our testing client
        self.socket_test_client = socket.test_client(app, flask_test_client= self.basic_test_client)

    def tearDown(self):
        """
        Tears down the connections already established
        """
        self.socket_test_client.disconnect()

    def test_connection(self):
        """
        Asserts that our socket client is connected
        """
        assert self.socket_test_client.is_connected()

    def test_broadcast(self):
        """
        Checks if the server is broadcasting chats correctly
        """
        self.socket_test_client.emit('message', {'username':'Bob','msg':'Hello'})
        receive_list = self.socket_test_client.get_received()  # receive the response from the emit
        assert len(receive_list) == 1
        assert receive_list[0]['name'] == 'message'
        assert receive_list[0]['args']['username'] == 'Bob'
        assert receive_list[0]['args']['msg'] == 'Hello'
    
    

if __name__ == '__main__':
    unittest.main()
