import pytest
import requests
from unittest.mock import MagicMock, call
from pipeline.api_client import APIClient

@pytest.fixture
def client() -> APIClient:
    """Returns a standard APIClient for testing."""
    return APIClient(base_url="http://test.com", pagination_limit=2)

def test_get_all_users_success(client: APIClient, mocker):
    """
    Tests a successful call to get_all_users.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": 1, "name": "Test User"}]
    mock_response.raise_for_status = MagicMock() # Mock to do nothing
    
    mock_get = mocker.patch('requests.get', return_value=mock_response)
    
    users = client.get_all_users()
    
    assert users == [{"id": 1, "name": "Test User"}]
    mock_get.assert_called_once_with("http://test.com/users", params=None)

def test_get_all_products_pagination(client: APIClient, mocker):
    """
    Tests the pagination logic for get_all_products.
    
    We will simulate 3 calls:
    1. Returns 2 products (the limit)
    2. Returns 1 product
    3. Returns an empty list (the stop signal)
    """
    page_1_data = [{"id": 1}, {"id": 2}]
    page_2_data = [{"id": 3}]
    page_3_data = []

    mock_response_1 = MagicMock()
    mock_response_1.json.return_value = page_1_data
    mock_response_1.raise_for_status = MagicMock()

    mock_response_2 = MagicMock()
    mock_response_2.json.return_value = page_2_data
    mock_response_2.raise_for_status = MagicMock()
    
    mock_response_3 = MagicMock()
    mock_response_3.json.return_value = page_3_data
    mock_response_3.raise_for_status = MagicMock()

    mock_get = mocker.patch('requests.get', side_effect=[
        mock_response_1, 
        mock_response_2, 
        mock_response_3
    ])

    products = client.get_all_products()

    assert products == [{"id": 1}, {"id": 2}, {"id": 3}]
    
    assert mock_get.call_count == 3
    
    expected_calls = [
        call("http://test.com/products", params={'limit': 2, 'page': 1}),
        call("http://test.com/products", params={'limit': 2, 'page': 2}),
        call("http://test.com/products", params={'limit': 2, 'page': 3}),
    ]
    assert mock_get.call_args_list == expected_calls

def test_api_http_error(client: APIClient, mocker):
    """
    Tests that the client returns None when an HTTPError occurs.
    """
    mock_get = mocker.patch('requests.get', 
                            side_effect=requests.exceptions.HTTPError("404 Not Found"))
    
    users = client.get_all_users()
    products = client.get_all_products()
    
    assert users is None
    assert products == [] 
    assert mock_get.call_count == 2

def test_url_sanitization():
    """
    Tests that the base_url is correctly sanitized (trailing slash removed).
    This test will FAIL until you add `.rstrip('/')` to the __init__.
    """
    client_with_slash = APIClient("http://test.com/", 5)
    client_without_slash = APIClient("http://test.com", 5)
    
    assert client_with_slash.base_url == "http://test.com"
    assert client_without_slash.base_url == "http://test.com"