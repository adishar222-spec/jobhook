import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_generate_cover_letter_missing_auth(client):
    rv = client.post('/api/cover-letter/generate', json={})
    assert rv.status_code == 401
