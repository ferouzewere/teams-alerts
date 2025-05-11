import pytest
from fastapi.testclient import TestClient
from fastapi.testclient import AsyncClient
import json
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_webflow_alert_success(mocker):
    # Mock the httpx post request
    mock_response = mocker.AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "Message sent successfully"
    
    mock_post = mocker.patch('httpx.AsyncClient.post', return_value=mock_response)

    # Test data
    test_payload = {
        "title": "Test Alert",
        "message": "This is a test message",
        "severity": "info"
    }

    # Make request to our endpoint
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/webflow-alert", json=test_payload)

    # Assertions
    assert response.status_code == 200
    assert response.json() == {
        "status": 200,
        "teams_response": "Message sent successfully"
    }
    
    # Verify the Teams webhook was called with correct data
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args.kwargs
    assert "json" in call_kwargs
    assert call_kwargs["headers"] == {"Content-Type": "application/json"}

@pytest.mark.asyncio
async def test_webflow_alert_with_minimal_data(mocker):
    # Mock the httpx post request
    mock_response = mocker.AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "Message sent successfully"
    
    mocker.patch('httpx.AsyncClient.post', return_value=mock_response)

    # Test with minimal data
    test_payload = {}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/webflow-alert", json=test_payload)

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_webflow_alert_teams_error(mocker):
    # Mock a failed Teams webhook request
    mock_response = mocker.AsyncMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    
    mocker.patch('httpx.AsyncClient.post', return_value=mock_response)

    test_payload = {
        "title": "Test Alert",
        "message": "This is a test message"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/webflow-alert", json=test_payload)

    assert response.status_code == 200  # Our API still returns 200
    assert response.json()["status"] == 500  # But includes Teams error status