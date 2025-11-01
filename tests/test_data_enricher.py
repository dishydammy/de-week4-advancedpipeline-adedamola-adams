import pytest
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from pipeline.data_enricher import DataEnricher

@pytest.fixture
def enricher() -> DataEnricher:
    """Returns an instance of DataEnricher."""
    return DataEnricher()

@pytest.fixture
def sample_products() -> List[Dict[str, Any]]:
    """Sample product data. Note the 'id' is the 'productId'."""
    return [
        {"id": 1, "title": "Product A", "price": "10.00", "category": "cat1"},
        {"id": 2, "title": "Product B", "price": "20.50", "category": "cat1"}
    ]

@pytest.fixture
def sample_users() -> List[Dict[str, Any]]:
    """Sample user data. Note the 'id' is the 'userId'."""
    return [
        {"id": 1, "username": "johndoe", "email": "john@test.com", "name": {"firstname": "John"}},
        {"id": 2, "username": "janedoe", "email": "jane@test.com", "name": {"firstname": "Jane"}}
    ]

@pytest.fixture
def sample_carts() -> List[Dict[str, Any]]:
    """Sample cart data. This is the 'bridge' table."""
    return [
        {
            "id": 101,
            "userId": 1,
            "products": [
                {"productId": 1, "quantity": 2},
                {"productId": 2, "quantity": 1}
            ]
        },
        {
            "id": 102,
            "userId": 99,
            "products": [
                {"productId": 1, "quantity": 3}
            ]
        },
        {
            "id": 103,
            "userId": 2,
            "products": [
                {"productId": 99, "quantity": 1}
            ]
        }
    ]

def test_successful_enrichment(enricher: DataEnricher, sample_products, sample_users, sample_carts):
    """
    Tests the full, successful merge of all three data sources.
    """
    enriched_df = enricher.enrich_data(sample_products, sample_users, sample_carts)
    
    assert enriched_df is not None
    assert len(enriched_df) == 4
    assert 'revenue' in enriched_df.columns
    assert 'username' in enriched_df.columns
    assert 'title' in enriched_df.columns
    
    row1 = enriched_df[
        (enriched_df['userId'] == 1) & (enriched_df['productId'] == 1)
    ].iloc[0]
    assert row1['quantity'] == 2
    assert row1['price'] == 10.00
    assert row1['revenue'] == 20.00
    assert row1['username'] == 'johndoe'
    assert row1['title'] == 'Product A'
    
    row2 = enriched_df[
        (enriched_df['userId'] == 1) & (enriched_df['productId'] == 2)
    ].iloc[0]
    assert row2['quantity'] == 1
    assert row2['price'] == 20.50
    assert row2['revenue'] == 20.50
    assert row2['username'] == 'johndoe'
    assert row2['title'] == 'Product B'

def test_missing_user_edge_case(enricher: DataEnricher, sample_products, sample_users, sample_carts):
    """
    Tests that a sale with a non-existent userId is kept,
    and its user columns are filled with NaN.
    """
    enriched_df = enricher.enrich_data(sample_products, sample_users, sample_carts)
    row_missing_user = enriched_df[enriched_df['userId'] == 99].iloc[0]
    
    assert row_missing_user['productId'] == 1
    assert row_missing_user['revenue'] == 30.00 
    assert pd.isna(row_missing_user['username'])
    assert pd.isna(row_missing_user['email'])

def test_missing_product_edge_case(enricher: DataEnricher, sample_products, sample_users, sample_carts):
    """
    Tests that a sale with a non-existent productId is kept,
    and its product columns are NaN and revenue is 0.
    """
    enriched_df = enricher.enrich_data(sample_products, sample_users, sample_carts)
    row_missing_product = enriched_df[enriched_df['productId'] == 99].iloc[0]
    
    assert row_missing_product['userId'] == 2
    assert row_missing_product['username'] == 'janedoe'
    assert pd.isna(row_missing_product['title'])
    assert row_missing_product['price'] == 0.0
    assert row_missing_product['revenue'] == 0.0

def test_empty_input_lists(enricher: DataEnricher, sample_products, sample_users, sample_carts):
    """
    Tests behavior when one of the input lists is empty.
    """
    df_no_carts = enricher.enrich_data(sample_products, sample_users, carts_list=[])
    assert df_no_carts is None
    
    df_no_products = enricher.enrich_data(products_list=[], users_list=sample_users, carts_list=sample_carts)
    assert df_no_products is None
    
    df_no_users = enricher.enrich_data(sample_products, users_list=[], carts_list=sample_carts)
    assert df_no_users is not None
    assert len(df_no_users) == 4
    assert pd.isna(df_no_users['username']).all()