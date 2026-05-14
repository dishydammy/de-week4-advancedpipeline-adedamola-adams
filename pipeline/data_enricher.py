import pandas as pd
import logging
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DataEnricher:
    """
    Handles the transformation and enrichment of raw product, user, and cart data.
    """

    def _flatten_carts(self, carts_df: pd.DataFrame) -> pd.DataFrame:
        """
        Flattens the nested 'products' list within the carts DataFrame.
        Each item in each cart becomes its own row.
        """
        if 'products' not in carts_df.columns or 'userId' not in carts_df.columns:
            logging.error("Carts data is missing 'products' or 'userId' columns.")
            return pd.DataFrame()

        logging.info("Flattening carts data...")
        
        exploded_df = carts_df.explode('products')
        products_normalized_df = pd.json_normalize(exploded_df['products'])
        
        flat_sales_df = pd.concat([
            exploded_df[['userId']].reset_index(drop=True),
            products_normalized_df
        ], axis=1)

        logging.info(f"Cart flattening complete. {len(flat_sales_df)} individual sales records created.")
        return flat_sales_df


    def enrich_data(self,
                      products_list: List[Dict[str, Any]],
                      users_list: List[Dict[str, Any]],
                      carts_list: List[Dict[str, Any]]) -> Optional[pd.DataFrame]:
        """
        Enriches sales (cart) data with product details and user (seller) info.
        """
        if not carts_list:
            logging.warning("Carts list is empty. No sales data to process.")
            return None
        if not products_list:
            logging.warning("Products list is empty. Cannot enrich sales data.")
            return None

        try:
            products_df = pd.DataFrame(products_list)
            users_df = pd.DataFrame(users_list)
            carts_df = pd.DataFrame(carts_list)
            sales_df = self._flatten_carts(carts_df)
            if sales_df.empty:
                logging.error("Failed to flatten cart data.")
                return None

            products_df = products_df.rename(columns={'id': 'productId'})
            
            sales_with_products_df = pd.merge(
                sales_df,
                products_df[['productId', 'price', 'title', 'category']],
                how='left',
                on='productId'
            )

            
            if not users_df.empty:
                users_df = users_df.rename(columns={'id': 'userId'})
                
                enriched_df = pd.merge(
                    sales_with_products_df,
                    users_df[['userId', 'username', 'email', 'name']],
                    how='left',
                    on='userId'
                )
            else:
                enriched_df = sales_with_products_df
                enriched_df['username'] = pd.NA
                enriched_df['email'] = pd.NA
                enriched_df['name'] = pd.NA
                
            enriched_df['price'] = pd.to_numeric(enriched_df['price'], errors='coerce').fillna(0)
            enriched_df['quantity'] = pd.to_numeric(enriched_df['quantity'], errors='coerce').fillna(0)
            
            enriched_df['revenue'] = enriched_df['price'] * enriched_df['quantity']
            
            logging.info(f"Data enrichment complete. {len(enriched_df)} total sales line items.")
            return enriched_df

        except Exception as e:
            logging.error(f"Error during data enrichment: {e}")
            return None