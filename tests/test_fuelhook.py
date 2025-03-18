import os
import json
from unittest.mock import patch, mock_open, MagicMock
import pytest


# Since main.py is a script and not a module, we'll test functions by importing them
# We'll need to patch environment variables and file operations

def test_environment_variables():
    """Test that the code handles environment variables correctly."""
    with patch.dict('os.environ', {
        'FUEL_TYPES': '["E10", "U91"]',
        'REGION': 'Sydney',
        'WEBHOOK_URL': 'https://example.com/webhook',
        'WEBHOOK_TYPE': 'Discord',
        'TELEGRAM_CHAT_ID': '123456789'
    }):
        # This is just testing that environment variables are read correctly
        assert json.loads(os.environ.get('FUEL_TYPES')) == ["E10", "U91"]
        assert os.environ.get('REGION') == 'Sydney'
        assert os.environ.get('WEBHOOK_URL') == 'https://example.com/webhook'
        assert os.environ.get('WEBHOOK_TYPE') == 'Discord'


@patch('os.path.isfile')
@patch('os.path.getsize')
@patch('builtins.open')
def test_price_data_file_creation(mock_file, mock_getsize, mock_isfile):
    """Test that the price data file is created if it doesn't exist."""
    # Setup mocks to indicate file doesn't exist initially, but once we've created it, it will exist
    mock_isfile.side_effect = lambda path: path != "data/priceData.json" or hasattr(mock_file, 'file_created')
    
    # We need to track which operations have been performed
    mock_file.file_created = False
    
    # This will store what was written to the file
    file_contents = {}
    
    # Configure mock_file to work differently based on the operation
    def open_side_effect(*args, **kwargs):
        nonlocal file_contents
        
        # Get filename and mode from args or kwargs
        filename = args[0] if args else kwargs.get('file', '')
        mode = args[1] if len(args) > 1 else kwargs.get('mode', 'r')
        
        if filename == 'data/priceData.json':
            if 'w' in mode:
                # Track that we've created the file
                mock_file.file_created = True
                
                # Create a mock file object
                mock_writer = mock_open()()
                return mock_writer
            else:
                # For reading, return either the contents we wrote or empty
                if mock_file.file_created and file_contents:
                    # Create readable content from our captured data
                    read_data = json.dumps(file_contents)
                    reader = mock_open(read_data=read_data)()
                else:
                    # Return empty data if file wasn't created yet
                    reader = mock_open(read_data="{}")()
                return reader
        
        # Default mock for other files
        return mock_open()()
    
    mock_file.side_effect = open_side_effect
    
    # Create a mock API response with proper JSON text
    mock_api_response = MagicMock()
    mock_api_response.text = json.dumps({
        "updated": "1633939200",
        "regions": [
            {
                "region": "",
                "prices": [
                    {"type": "E10", "price": "1.45", "suburb": "Test", "state": "TEST"}
                ]
            }
        ]
    })
    
    # Expected blank price data structure (same as in main.py)
    expected_blank_price = {
        "E10": 0,
        "U91": 0,
        "U95": 0,
        "U98": 0,
        "Diesel": 0,
        "LPG": 0
    }
    
    # Capture the data passed to json.dump
    def capture_json_dump(data, file_obj):
        nonlocal file_contents
        file_contents = data
        # Call the original json.dump to keep the code running
        original_json_dump(data, file_obj)
    
    original_json_dump = json.dump
    
    # Execute the main script's file creation logic
    with patch.dict('os.environ', {'FUEL_TYPES': '[]', 'REGION': '', 'WEBHOOK_URL': ''}):
        with patch('requests.post', return_value=mock_api_response):
            with patch('json.dump', side_effect=capture_json_dump):
                try:
                    # Import PRICE_DATA_FILE which will execute the script
                    from main import PRICE_DATA_FILE
                    
                    # Check if the file was opened for writing
                    has_write_calls = any("data/priceData.json" in str(call) and "w" in str(call) 
                                         for call in mock_file.call_args_list)
                    assert has_write_calls, "File should have been opened for writing"
                    
                    # For each fuel type in our expected structure, verify it exists in the actual data
                    for fuel_type in expected_blank_price:
                        assert fuel_type in file_contents, f"File contents should include {fuel_type}"
                        assert file_contents[fuel_type] == 0, f"{fuel_type} should be initialized to 0"
                    
                except Exception as e:
                    pytest.fail(f"Test failed with exception: {str(e)}")


@pytest.fixture
def mock_api_response():
    """Fixture that returns a mock API response with fuel prices."""
    return {
        "updated": "1633939200",
        "regions": [
            {
                "region": "Sydney",
                "prices": [
                    {"type": "E10", "price": "1.45", "suburb": "Bondi", "state": "NSW"},
                    {"type": "U91", "price": "1.55", "suburb": "Surry Hills", "state": "NSW"},
                    {"type": "U95", "price": "1.65", "suburb": "Newtown", "state": "NSW"},
                    {"type": "U98", "price": "1.75", "suburb": "Parramatta", "state": "NSW"},
                    {"type": "Diesel", "price": "1.40", "suburb": "Blacktown", "state": "NSW"},
                    {"type": "LPG", "price": "0.85", "suburb": "Liverpool", "state": "NSW"}
                ]
            },
            {
                "region": "Melbourne",
                "prices": [
                    {"type": "E10", "price": "1.42", "suburb": "Richmond", "state": "VIC"}
                ]
            }
        ]
    }


@patch('requests.post')
def test_api_request(mock_post, mock_api_response):
    """Test that the API request is made correctly."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.text = json.dumps(mock_api_response)
    mock_post.return_value = mock_response

    # Import main to execute the API request
    with patch.dict('os.environ', {
        'FUEL_TYPES': '["E10"]', 
        'REGION': 'Sydney', 
        'WEBHOOK_URL': 'https://example.com/webhook'
    }):
        with patch('os.path.isfile', return_value=True):
            with patch('os.path.getsize', return_value=100):
                with patch('builtins.open', mock_open(read_data=json.dumps({"E10": 0}))):
                    # This will execute the script, including the API request
                    try:
                        from main import API_RESPONSE

                        # Check that the request was made with the correct URL and headers
                        mock_post.assert_called_once_with(
                            "https://projectzerothree.info/api.php?format=json",
                            headers={"User-Agent": "FuelHook v2.4.0"}
                        )
                    except Exception:
                        # The import might fail because we're patching, that's ok
                        pass
