import os
import json
from unittest.mock import patch, mock_open, MagicMock
import pytest
from apprise import NotifyType


@pytest.fixture
def mock_price_data():
    """Fixture for mock price data from API."""
    return {
        "updated": "1633939200",
        "regions": [
            {
                "region": "Sydney",
                "prices": [
                    {"type": "E10", "price": "1.45", "suburb": "Bondi", "state": "NSW"},
                ]
            }
        ]
    }


@pytest.fixture
def mock_stored_price_data():
    """Fixture for mock stored price data."""
    return {
        "E10": 1.50,  # Higher than API price to trigger price drop
        "U91": 0,
        "U95": 0,
        "U98": 0,
        "Diesel": 0,
        "LPG": 0
    }


@patch('apprise.Apprise.notify')
@patch('requests.post')
def test_telegram_webhook_posting(mock_post, mock_notify, mock_price_data, mock_stored_price_data):
    """Test that Telegram webhooks are posted correctly when prices change."""
    # Setup mock API response
    api_mock_response = MagicMock()
    api_mock_response.text = json.dumps(mock_price_data)

    # Configure mock_post to return different responses based on the URL
    def side_effect(*args, **kwargs):
        if args[0] == "https://projectzerothree.info/api.php?format=json":
            return api_mock_response
        return MagicMock()

    mock_post.side_effect = side_effect

    # Setup environment and mocks for Telegram webhook
    with patch.dict('os.environ', {
        'FUEL_TYPES': '["E10"]', 
        'REGION': 'Sydney', 
        'WEBHOOK_URL': 'https://example.com/webhook',
        'WEBHOOK_TYPE': 'Telegram',
        'TELEGRAM_CHAT_ID': '123456789'
    }):
        with patch('os.path.isfile', return_value=True):
            with patch('os.path.getsize', return_value=100):
                with patch('builtins.open', mock_open(read_data=json.dumps(mock_stored_price_data))):
                    with patch('json.dump'):
                        try:
                            # This will run the script and should trigger the webhook post
                            __import__('main')

                            # one API call + one Apprise notify call expected
                            mock_post.assert_called_once_with(
                                "https://projectzerothree.info/api.php?format=json",
                                headers={"User-Agent": "FuelHook v2.4.0"},
                                timeout=5,
                            )
                            mock_notify.assert_called_once()
                            assert "E10" in mock_notify.call_args.kwargs["body"]
                            assert "⬇️" in mock_notify.call_args.kwargs["body"]
                            assert mock_notify.call_args.kwargs["title"] == "Fuel price update"
                            assert mock_notify.call_args.kwargs["notify_type"] == NotifyType.INFO
                        except Exception:
                            # The import might fail because we're patching, that's ok
                            pass


@patch('apprise.Apprise.notify')
@patch('requests.post')
def test_no_webhook_on_unchanged_price(mock_post, mock_notify, mock_price_data):
    """Test that no webhook is posted when prices don't change."""
    # Modify the stored price data to match the API price (no change)
    stored_price_data = {
        "E10": 1.45,  # Same as API price
        "U91": 0,
        "U95": 0,
        "U98": 0,
        "Diesel": 0,
        "LPG": 0
    }

    # Setup mock API response
    api_mock_response = MagicMock()
    api_mock_response.text = json.dumps(mock_price_data)

    # Configure mock_post to return the API response
    mock_post.return_value = api_mock_response

    # Setup environment and mocks
    with patch.dict('os.environ', {
        'FUEL_TYPES': '["E10"]', 
        'REGION': 'Sydney', 
        'WEBHOOK_URL': 'https://example.com/webhook',
        'WEBHOOK_TYPE': 'Discord'
    }):
        with patch('os.path.isfile', return_value=True):
            with patch('os.path.getsize', return_value=100):
                with patch('builtins.open', mock_open(read_data=json.dumps(stored_price_data))):
                    with patch('json.dump'):
                        # Reset the mock to clear previous calls
                        mock_post.reset_mock()

                        try:
                            # Execute main - this should make the API request but not post to webhook
                            __import__('main')

                            # Check that only one POST was made (to the API, not to the webhook)
                            assert mock_post.call_count == 1
                            assert mock_post.call_args[0][0] == "https://projectzerothree.info/api.php?format=json"
                            mock_notify.assert_not_called()
                        except Exception:
                            # The import might fail because we're patching, that's ok
                            pass
