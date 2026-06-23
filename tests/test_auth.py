import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_login_missing_fields(client):
    rv = client.post('/api/auth/login', json={})
    assert rv.status_code == 400
