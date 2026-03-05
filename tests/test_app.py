import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_endpoint(client):
    response = client.get('/')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'message' in data
    assert data['version'] == '1.0.0'

def test_health_endpoint(client):
    response = client.get('/health')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['status'] == 'healthy'

def test_echo_endpoint(client):
    test_data = {'test': 'data'}
    response = client.post('/api/echo', 
                          json=test_data,
                          content_type='application/json')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['received'] == test_data
    assert data['echo'] == 'success'
