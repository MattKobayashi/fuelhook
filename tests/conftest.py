import pytest

@pytest.fixture
def mock_response():
    """A fixture that mimics a successful API response."""
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.text = str(json_data)
            
        def json(self):
            return self.json_data
    
    return MockResponse({"status": "success", "data": {"fuel_price": 1.45}}, 200)
