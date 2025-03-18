import pytest
import requests

def test_requests_import():
    """Test that requests can be imported properly."""
    assert requests.__name__ == "requests"

def test_mock_api_call(monkeypatch, mock_response):
    """Test a mocked API call."""
    def mock_get(*args, **kwargs):
        return mock_response
    
    # Apply the monkeypatch to replace requests.get with mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    
    # Make the API call
    response = requests.get("https://api.example.com/fuel")
    
    # Assert the expected behavior
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "fuel_price" in response.json()["data"]
