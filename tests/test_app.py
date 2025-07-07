import io
import pytest
from app import app

def create_file(filename, content, mimetype):
    return (io.BytesIO(content.encode()), filename, mimetype)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_get(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b'<form' in response.data

def test_upload_txt_file(client):
    data = {
        'file_input': create_file('test.txt', 'Hello world', 'text/plain')
    }
    response = client.post('/', data=data, content_type='multipart/form-data')
    assert b"uploaded successfully" in response.data or b"response" in response.data

def test_upload_wrong_mime(client):
    data = {
        'file_input': create_file('test.txt', 'Hello world', 'application/pdf')
    }
    response = client.post('/', data=data, content_type='multipart/form-data')
    assert b'Niedozwolony typ MIME' in response.data

def test_upload_unsupported_extension(client):
    data = {
        'file_input': create_file('test.exe', 'fake', 'application/octet-stream')
    }
    response = client.post('/', data=data, content_type='multipart/form-data')
    assert b'Only .txt, .docx, .pdf, .csv, .xlsx, and .zip files are supported.' in response.data

def test_upload_too_large(client):
    big_content = 'a' * (21 * 1024 * 1024)  # 21MB
    data = {
        'file_input': (io.BytesIO(big_content.encode()), 'big.txt', 'text/plain')
    }
    response = client.post('/', data=data, content_type='multipart/form-data')
    assert response.status_code == 413
    assert b'Maksymalny rozmiar to 20MB' in response.data
