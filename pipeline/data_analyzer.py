import pandas as pd
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DataAnalyzer:
    """
    Analyzes the enriched DataFrame to generate performance insights.
    """

    def analyze(self, enriched_df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Calculates performance metrics for each seller.
        """
        if enriched_df is None or enriched_df.empty:
            logging.warning("Received empty or None DataFrame. Skipping analysis.")
            return None
            
        if 'username' not in enriched_df.columns:
            logging.error("Missing 'username' column for analysis.")
            return None

        analyzable_df = enriched_df.dropna(subset=['username'])
        if analyzable_df.empty:
            logging.warning("No data with valid usernames found. No analysis to perform.")
            return {}

        logging.info(f"Analyzing {len(analyzable_df)} sales records...")

        try:
            analysis_df = analyzable_df.groupby('username').agg(
                total_revenue=('revenue', 'sum'),
                total_products_sold=('quantity', 'sum'),
                average_product_price=('price', 'mean')
            )

            analysis_df['total_revenue'] = analysis_df['total_revenue'].round(2)
            analysis_df['average_product_price'] = analysis_df['average_product_price'].round(2)
            analysis_df['total_products_sold'] = analysis_df['total_products_sold'].astype(int)

            logging.info("Analysis complete.")
            return analysis_df.to_dict(orient='index')

        except Exception as e:
            logging.error(f"Error during data analysis: {e}")
            return None