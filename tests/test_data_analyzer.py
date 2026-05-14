import pytest
import pandas as pd
from pipeline.data_analyzer import DataAnalyzer

@pytest.fixture
def analyzer() -> DataAnalyzer:
    """Returns an instance of DataAnalyzer."""
    return DataAnalyzer()

@pytest.fixture
def sample_enriched_data() -> pd.DataFrame:
    """
    A fixture to simulate the output of the DataEnricher.
    """
    data = {
        'username': ['johndoe', 'johndoe', 'janedoe', 'johndoe', None],
        'quantity': [2, 1, 5, 1, 10],
        'price':    [10.0, 20.0, 5.0, 10.0, 100.0],
        'revenue':  [20.0, 20.0, 25.0, 10.0, 1000.0]
    }
    return pd.DataFrame(data)

def test_analysis_success(analyzer: DataAnalyzer, sample_enriched_data: pd.DataFrame):
    """
    Tests that the aggregation logic correctly calculates stats per seller.
    """
    report = analyzer.analyze(sample_enriched_data)

    assert report is not None
    assert 'johndoe' in report
    assert 'janedoe' in report
    assert None not in report 

    john_stats = report['johndoe']
    assert john_stats['total_revenue'] == 50.0  
    assert john_stats['total_products_sold'] == 4
    assert john_stats['average_product_price'] == 13.33
    
    jane_stats = report['janedoe']
    assert jane_stats['total_revenue'] == 25.0
    assert jane_stats['total_products_sold'] == 5
    assert jane_stats['average_product_price'] == 5.0

def test_analysis_empty_input(analyzer: DataAnalyzer):
    """
    Tests that the analyzer handles empty or None inputs gracefully.
    """
    assert analyzer.analyze(pd.DataFrame()) is None
    assert analyzer.analyze(None) is None

def test_analysis_no_valid_usernames(analyzer: DataAnalyzer):
    """
    Tests behavior when the dataframe only contains NaN usernames.
    """
    data = {
        'username': [None, None],
        'quantity': [1, 1],
        'price':    [10.0, 20.0],
        'revenue':  [10.0, 20.0]
    }
    df = pd.DataFrame(data)
    
    report = analyzer.analyze(df)
    assert report == {}