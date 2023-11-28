import unittest
from src import app, db
from src.models import User
from flask_testing import TestCase
from flask import url_for
class MyTestCase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        with self.app.app_context():
            db.create_all()
            self.user = User(username='test', first_name='hi', last_name='no',
                             email='kwiatk@msu.edu', password='tester')
            #  adds the above user to the database
            db.session.add(self.user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_landing_page_failure(self):
        self.client.get('/')
        #  not logged in so we get sent back
        self.assert_template_used('landing_page.html')

    def test_landing_page_loggedIN(self):
        # Log in the user
        self.client.post('/login', data={'username': 'test', 'password': 'tester'})

        # Check if the expected template is used in the final response
        #  self.assert_template_used('search.html')

    def test_successful_login(self):
        response = self.client.post('/login',
                                    data={'username': 'test', 'password': 'tester'})
        self.assert_template_used('search.html')

    def test_login_page(self):
        self.client.get('login')
        self.assertTemplateUsed('login.html')

if __name__ == '__main__':
    unittest.main()
