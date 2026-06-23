import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_score_missing_fields(client):
    rv = client.post('/api/ats/score', json={})
    assert rv.status_code == 401 # Unauthorized first
