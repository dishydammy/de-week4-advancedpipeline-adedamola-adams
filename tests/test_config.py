import pytest
from pathlib import Path
from pipeline.config import ConfigManager

# This is the content written to the temporary config file
FAKE_CONFIG_CONTENT = """
[api]
base_url = https://fake-api-url.com
pagination_limit = 10

[output]
filename = test_report.json
"""

@pytest.fixture
def fake_config_file(tmp_path: Path) -> str:
    """
    A pytest fixture that creates a temporary config file
    with known content and returns the path to it.
    """
    config_file = tmp_path / "test_pipeline.cfg"
    config_file.write_text(FAKE_CONFIG_CONTENT)
    return str(config_file)

def test_config_manager_load_success(fake_config_file: str):
    """
    Tests that the ConfigManager can successfully load a valid config file.
    """
    manager = ConfigManager(config_path=fake_config_file)
    api_config = manager.get_api_config()
    output_config = manager.get_output_config()

    assert api_config['base_url'] == "https://fake-api-url.com"
    assert api_config['pagination_limit'] == 10
    assert output_config['filename'] == "test_report.json"
    
def test_config_manager_file_not_found():
    """
    Tests that ConfigManager raises FileNotFoundError for a non-existent file.
    """
    with pytest.raises(FileNotFoundError):
        ConfigManager(config_path="non_existent_file.cfg")

def test_config_manager_missing_section(tmp_path: Path):
    """
    Tests that ConfigManager raises a ValueError if a section is missing.
    """
    bad_config_content = """
[output]
filename = test_report.json
"""
    config_file = tmp_path / "bad_config.cfg"
    config_file.write_text(bad_config_content)
    
    manager = ConfigManager(config_path=str(config_file))
    
    with pytest.raises(ValueError, match="Invalid config file"):
        manager.get_api_config()

def test_config_manager_missing_key(tmp_path: Path):
    """
    Tests that ConfigManager raises a ValueError if a key is missing.
    """
    bad_config_content = """
[api]
base_url = https://fake-api-url.com
# pagination_limit is missing
"""
    config_file = tmp_path / "bad_config.cfg"
    config_file.write_text(bad_config_content)
    
    manager = ConfigManager(config_path=str(config_file))
    
    with pytest.raises(ValueError, match="Invalid config file"):
        manager.get_api_config() 