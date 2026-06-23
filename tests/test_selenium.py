import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_apply_prepare_unauth(client):
    rv = client.post('/api/apply/prepare', json={})
    assert rv.status_code == 401
