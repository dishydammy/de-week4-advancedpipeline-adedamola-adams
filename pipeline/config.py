import configparser
import logging
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path: str = "pipeline.cfg"):
        """
        Initializes the ConfigManager by reading a configuration file.
        """
        if not Path(config_path).exists():
            logging.error(f"Configuration file not found at: {config_path}")
            raise FileNotFoundError(f"Config file not found: {config_path}")

        self.parser = configparser.ConfigParser()
        self.parser.read(config_path)
        logging.info(f"Successfully loaded configuration from {config_path}")
    
    def get_api_config(self) -> dict:
        """
        Retrieves the [api] section from the config.
        """
        try:
            return {
                'base_url': self.parser.get('api', 'base_url'),
                'pagination_limit': self.parser.getint('api', 'pagination_limit')
            }
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            logging.error(f"Missing 'api' section or options in config: {e}")
            raise ValueError(f"Invalid config file: {e}")
    
    def get_output_config(self) -> dict:
        """
        Retrieves the [output] section from the config.
        """
        try:
            return {
                'filename': self.parser.get('output', 'filename')
            }
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            logging.error(f"Missing 'output' section or options in config: {e}")
            raise ValueError(f"Invalid config file: {e}")
