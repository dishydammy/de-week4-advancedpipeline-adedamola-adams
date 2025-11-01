import pytest
from unittest.mock import MagicMock, patch

from pipeline.pipeline import Pipeline

CONFIG_PATH = 'pipeline.pipeline.ConfigManager'
CLIENT_PATH = 'pipeline.pipeline.APIClient'
ENRICHER_PATH = 'pipeline.pipeline.DataEnricher'
ANALYZER_PATH = 'pipeline.pipeline.DataAnalyzer'
JSON_DUMP_PATH = 'json.dump'
OPEN_PATH = 'builtins.open'


@pytest.fixture
def mock_components(mocker):
    """
    A fixture that mocks all the pipeline's dependencies.
    """
    mock_config_manager = mocker.patch(CONFIG_PATH, autospec=True)
    mock_api_client = mocker.patch(CLIENT_PATH, autospec=True)
    mock_data_enricher = mocker.patch(ENRICHER_PATH, autospec=True)
    mock_data_analyzer = mocker.patch(ANALYZER_PATH, autospec=True)
    
    mock_open = mocker.patch(OPEN_PATH, mocker.mock_open())
    mock_json_dump = mocker.patch(JSON_DUMP_PATH)
    
    # Config setup
    mock_config = mock_config_manager.return_value
    mock_config.get_api_config.return_value = {
        'base_url': 'http://fake.com',
        'pagination_limit': 5
    }
    mock_config.get_output_config.return_value = {'filename': 'fake_report.json'}
    
    # API setup
    mock_api = mock_api_client.return_value
    mock_api.get_all_users.return_value = [{'id': 1, 'name': 'User'}]
    mock_api.get_all_products.return_value = [{'id': 101, 'price': 10}]
    mock_api.get_all_carts.return_value = [{'userId': 1, 'products': []}]
    
    # Enricher setup
    mock_enricher = mock_data_enricher.return_value
    mock_enricher.enrich_data.return_value = MagicMock(name="MockEnrichedData")
    
    mock_analyzer = mock_data_analyzer.return_value
    mock_analyzer.analyze.return_value = {'johndoe': {'total_revenue': 100}}

    return {
        'config': mock_config,
        'api': mock_api,
        'enricher': mock_enricher,
        'analyzer': mock_analyzer,
        'json_dump': mock_json_dump
    }


def test_pipeline_run_success(mock_components, mocker):
    """
    Tests the successful .run() method of the pipeline,
    ensuring all components are called in the correct order.
    """
    pipeline = Pipeline(config_path="fake.cfg")
    pipeline.run()

    api = mock_components['api']
    enricher = mock_components['enricher']
    analyzer = mock_components['analyzer']
    json_dump = mock_components['json_dump']

    api.get_all_users.assert_called_once()
    api.get_all_products.assert_called_once()
    api.get_all_carts.assert_called_once()
    
    enricher.enrich_data.assert_called_once_with(
        api.get_all_products.return_value,
        api.get_all_users.return_value,
        api.get_all_carts.return_value
    )
    
    analyzer.analyze.assert_called_once_with(
        enricher.enrich_data.return_value
    )
    
    json_dump.assert_called_once_with(
        analyzer.analyze.return_value, 
        mocker.ANY, 
        indent=4
    )


def test_pipeline_api_fetch_failure(mock_components):
    """
    Tests that the pipeline stops if a critical API fetch fails.
    """
    api = mock_components['api']
    api.get_all_carts.return_value = []

    enricher = mock_components['enricher']
    analyzer = mock_components['analyzer']

    pipeline = Pipeline(config_path="fake.cfg")
    pipeline.run()
    
    enricher.enrich_data.assert_not_called()
    analyzer.analyze.assert_not_called()