import requests
import logging
from typing import Union, Optional, List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class APIClient:
    """
    A client to handle communication with the FakestoreAPI,
    including pagination and error handling for all data sources.
    """

    def __init__(self, base_url: str, pagination_limit: int):
        """
        Initializes the API Client with settings from the config.
        """
        if not base_url:
            raise ValueError("Base URL cannot be empty.")
        if not pagination_limit or pagination_limit <= 0:
            raise ValueError("Pagination limit must be a positive integer.")
            
        self.base_url = base_url.rstrip('/')  # Remove trailing slash
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
        except requests.exceptions.RequestException as req_err:
            logging.error(f"An error occurred during request to {url}: {req_err}")
            return None

    def get_all_users(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetches all users from the API.
        """
        return self._make_request("/users")  # type: ignore

    def _fetch_paginated_data(self, endpoint: str) -> List[Dict[str, Any]]:
        """
        A generic helper to fetch all data from a paginated endpoint.
        """
        all_data: List[Dict[str, Any]] = []
        page = 1
        
        while True:
            logging.info(f"Fetching {endpoint} page {page}...")
            params = {
                'limit': self.pagination_limit,
                'page': page 
            }
            
            data = self._make_request(endpoint, params=params)
            
            if data is None:
                logging.error(f"Failed to fetch {endpoint} page. Stopping pagination.")
                break
                
            if not data:
                logging.info(f"Reached end of {endpoint} list. Pagination complete.")
                break
                
            all_data.extend(data)
            page += 1
            
        return all_data

    def get_all_products(self) -> List[Dict[str, Any]]:
        """
        Fetches all products from the API, handling pagination.
        """
        return self._fetch_paginated_data("/products")

    def get_all_carts(self) -> List[Dict[str, Any]]:
        """
        Fetches all carts from the API, handling pagination.
        This is the "bridge" data connecting users to products.
        """
        return self._fetch_paginated_data("/carts")