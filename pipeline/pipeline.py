import json
import logging
from .config import ConfigManager
from .api_client import APIClient
from .data_enricher import DataEnricher
from .data_analyzer import DataAnalyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Pipeline:
    """
    Orchestrates the entire ETL workflow from data extraction
    to analysis and report generation.
    """
    def __init__(self, config_path: str = "pipeline.cfg"):
        """
        Initializes the pipeline by loading the configuration
        and setting up all necessary components.
        """
        logging.info("Initializing pipeline...")
        try:
            self.config_manager = ConfigManager(config_path)
            
            api_config = self.config_manager.get_api_config()
            self.api_client = APIClient(
                base_url=api_config['base_url'],
                pagination_limit=api_config['pagination_limit']
            )
            
            self.output_config = self.config_manager.get_output_config()
            self.data_enricher = DataEnricher()
            self.data_analyzer = DataAnalyzer()
            
            logging.info("Pipeline initialized successfully.")
            
        except FileNotFoundError:
            logging.error(f"CRITICAL: Config file not found at {config_path}. Pipeline cannot start.")
            raise
        except (ValueError, KeyError) as e:
            logging.error(f"CRITICAL: Error in config file: {e}. Pipeline cannot start.")
            raise

    def run(self):
        """
        Executes the full ETL pipeline.
        1. Extract data from all API endpoints.
        2. Transform and enrich the data.
        3. Analyze the enriched data.
        4. Load (save) the final report.
        """
        try:
            logging.info("Starting (E)xtract phase...")
            users = self.api_client.get_all_users()
            products = self.api_client.get_all_products()
            carts = self.api_client.get_all_carts()
            
            if users is None or not products or not carts:
                logging.error("Failed to fetch one or more critical data sources. Aborting pipeline.")
                return
            logging.info("Extract phase complete.")
        
            logging.info("Starting (T)ransform phase...")
            enriched_data = self.data_enricher.enrich_data(products, users, carts)
            
            if enriched_data is None:
                logging.error("Data enrichment failed. Aborting pipeline.")
                return
            logging.info("Transform phase complete.")

            logging.info("Starting Analysis phase...")
            analysis_report = self.data_analyzer.analyze(enriched_data)
            
            if analysis_report is None:
                logging.error("Data analysis failed. Aborting pipeline.")
                return
            logging.info("Analysis phase complete.")

            logging.info("Starting (L)oad phase...")
            output_filename = self.output_config['filename']
            with open(output_filename, 'w') as f:
                json.dump(analysis_report, f, indent=4)
            logging.info(f"Successfully saved report to {output_filename}")
            logging.info("Pipeline run complete.")

        except Exception as e:
            logging.error(f"An unexpected error occurred during pipeline run: {e}", exc_info=True)