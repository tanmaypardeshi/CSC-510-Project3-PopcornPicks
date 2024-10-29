import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))  # 将上一级目录加入sys.path
from src.search import Search  # 导入上一级目录中的模块
import pytest
from flask import Flask
import requests
from app import app as flask_app

@pytest.fixture
def client():
    with flask_app.test_client() as client:
        yield client

def test_new_series_status_code(client):
    response = client.get('/new_series')
    assert response.status_code == 200

def test_new_series_content_type(client):
    response = client.get('/new_series')
    assert response.content_type == 'text/html; charset=utf-8'

def test_new_series_template_used(client):
    response = client.get('/new_series')
    assert b"New Series Coming Soon!" in response.data

def test_new_series_no_series(client):
    response = client.get('/new_series')
    assert b"Could not fetch new series" not in response.data

def test_new_series_series_list(client):
    response = client.get('/new_series')
    assert b"New Releases:" in response.data

def test_new_series_series_item(client):
    response = client.get('/new_series')
    assert b"Release Date:" in response.data

def test_new_series_series_name(client):
    response = client.get('/new_series')
    assert b"Series Name" not in response.data  # Assuming "Series Name" is not a placeholder

def test_new_series_series_date(client):
    response = client.get('/new_series')
    assert b"2023-01-01" not in response.data  # Assuming "2023-01-01" is not a placeholder

def test_new_series_show_message(client):
    response = client.get('/new_series')
    assert b"Could not fetch new series" not in response.data

def test_new_series_user_logged_in(client):
    with client.session_transaction() as session:
        session['user_id'] = 1  # Assuming user_id 1 is logged in
    response = client.get('/new_series')
    assert response.status_code == 200

def test_new_series_user_not_logged_in(client):
    with client.session_transaction() as session:
        session.pop('user_id', None)
    response = client.get('/new_series')
    assert response.status_code == 302  # Redirect to login

def test_new_series_pagination(client):
    response = client.get('/new_series?page=2')
    assert response.status_code == 200

def test_new_series_invalid_page(client):
    response = client.get('/new_series?page=invalid')
    assert response.status_code == 200

def test_new_series_api_key_missing(client):
    # Temporarily remove API key
    original_key = flask_app.config['TMDB_API_KEY']
    flask_app.config['TMDB_API_KEY'] = ''
    response = client.get('/new_series')
    flask_app.config['TMDB_API_KEY'] = original_key
    assert b"Could not fetch new series" in response.data

def test_new_series_api_timeout(client, monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.exceptions.Timeout()
    monkeypatch.setattr('requests.get', mock_get)
    response = client.get('/new_series')
    assert b"Could not fetch new series" in response.data

def test_new_series_api_connection_error(client, monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.exceptions.ConnectionError()
    monkeypatch.setattr('requests.get', mock_get)
    response = client.get('/new_series')
    assert b"Could not fetch new series" in response.data

def test_new_series_api_http_error(client, monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.exceptions.HTTPError()
    monkeypatch.setattr('requests.get', mock_get)
    response = client.get('/new_series')
    assert b"Could not fetch new series" in response.data

def test_new_series_api_request_exception(client, monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.exceptions.RequestException()
    monkeypatch.setattr('requests.get', mock_get)
    response = client.get('/new_series')
    assert b"Could not fetch new series" in response.data

def test_new_series_failing_test(client):
    response = client.get('/new_series')
    assert b"Non-existent text" in response.data  # This test is designed to fail

def test_new_series_successful_fetch(client, monkeypatch):
    class MockResponse:
        @staticmethod
        def json():
            return {'results': [{'name': 'Mock Series', 'first_air_date': '2023-01-01'}]}
        status_code = 200
    monkeypatch.setattr('requests.get', lambda *args, **kwargs: MockResponse())
    response = client.get('/new_series')
    assert b"Mock Series" in response.data
    assert b"2023-01-01" in response.data