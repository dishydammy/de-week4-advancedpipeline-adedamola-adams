import requests
import logging
from typing import Union, Optional, List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class APIClient:
    """
    A client to handle communication with the FakestoreAPI
    """

    def __init__(self, base_url: str, pagination_limit: int):
        """
        Initializes the API Client with settings from the config.
        """
        if not base_url:
            raise ValueError("Base URL cannot be empty.")
        if not pagination_limit or pagination_limit <= 0:
            raise ValueError("Pagination limit must be a positive integer.")
            
        self.base_url = base_url
        self.pagination_limit = pagination_limit
        logging.info(f"APIClient initialized for {self.base_url} with limit {self.pagination_limit}")

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Union[list, dict, None]:
        """
        A private helper method to handle the actual HTTP request and error handling.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logging.info(f"Making GET request to: {url} with params: {params}")

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err} for URL: {url}")
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Connection error occurred: {conn_err} for URL: {url}")
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout error occurred: {timeout_err} for URL: {url}")
        except requests.exceptions.RequestException as req_err:
            logging.error(f"An unexpected error occurred: {req_err} for URL: {url}")

        return None

    def get_all_users(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetches all users from the API.
        """
        return self._make_request("/users")  # type: ignore

    def get_all_products(self) -> List[Dict[str, Any]]:
        """
        Fetches all products from the API, handling pagination.
        """
        all_products: List[Dict[str, Any]] = []
        page = 1
        
        while True:
            logging.info(f"Fetching products page {page}...")
            params = {
                'limit': self.pagination_limit,
                'page': page
            }
            
            data = self._make_request("/products", params=params)
            
            if data is None:
                logging.error("Failed to fetch products page. Stopping pagination.")
                break
                
            if not data:
                logging.info("Reached end of product list. Pagination complete.")
                break
                
            all_products.extend(data)
            page += 1
            
        return all_products