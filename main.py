import sys
import logging
from pipeline.pipeline import Pipeline

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

def main():
    """
    Main function to initialize and run the data enrichment pipeline.
    """
    logging.info("Starting OmniCart Analytics pipeline...")
    
    try:
        # 1. Initialize the pipeline
        pipeline = Pipeline(config_path="pipeline.cfg")
        
        # 2. Run the pipeline
        pipeline.run()
        
    except FileNotFoundError:
        logging.critical("Pipeline startup failed: pipeline.cfg not found.")
        sys.exit(1) 
    except (ValueError, KeyError) as e:
        logging.critical(f"Pipeline startup failed: Invalid configuration. {e}")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"An unexpected critical error occurred: {e}", exc_info=True)
        sys.exit(1)

    logging.info("OmniCart Analytics pipeline finished successfully.")

if __name__ == "__main__":
    main()