# OmniCart Analytics - Seller Performance Pipeline

This project is a Python-based ETL pipeline that fetches data from the fakestoreapi.com API, enriches it to combine sales, product, and seller information, and analyzes the data to generate a seller performance report.

## Overview

The pipeline consists of several components:
- **API Client**: Fetches data from external API endpoints
- **Data Enricher**: Combines and enriches data from multiple sources
- **Data Analyzer**: Generates seller performance metrics
- **Configuration**: Manages pipeline settings and parameters

## Pagination Strategy

The assignment required implementing a pagination loop. However, after investigation, it was confirmed that the fakestoreapi.com does not support pagination parameters like `page`, `skip`, or `offset`. Any attempt to use them results in an infinite loop as the API repeatedly returns the first page of data.

To solve this, the APIClient implements the only viable workaround: it makes one single, full request for each endpoint (`/users`, `/products`, `/carts`) to fetch all the data at once. This avoids the infinite loop and allows the pipeline to proceed.

## Data Enrichment Logic

The core challenge is that product data does not contain a `userId`. To link sellers to the products they sold, a three-source merge is required:

- **`/users`**: Provides the seller (user) information (e.g., username, email).
- **`/products`**: Provides the product information (e.g., price, title).
- **`/carts`**: Acts as the "bridge" or "sales" table. It's the only endpoint that links a `userId` to a list of `productIds` and the quantity sold.

The DataEnricher component first flattens the nested carts data, then merges it with products (on `productId`) and users (on `userId`) to create a single, enriched DataFrame.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Pipeline

Execute the main pipeline:

```bash
python main.py
```

This will create the `seller_performance_report.json` file in the root directory.

### Running Tests

Run the test suite:

```bash
pytest
```

## Project Structure

```
.
├── main.py                 # Entry point for the pipeline
├── pipeline.cfg           # Configuration file
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── pipeline/             # Main pipeline package
│   ├── __init__.py
│   ├── api_client.py     # API data fetching
│   ├── config.py         # Configuration management
│   ├── data_analyzer.py  # Data analysis and reporting
│   ├── data_enricher.py  # Data enrichment and merging
│   └── pipeline.py       # Main pipeline orchestration
└── tests/                # Test suite
    ├── __init__.py
    ├── test_api_client.py
    ├── test_config.py
    ├── test_data_analyzer.py
    ├── test_data_enricher.py
    └── test_pipeline.py
```

## Configuration

The pipeline can be configured using the `pipeline.cfg` file. Key configuration options include:
- API endpoints and settings
- Data processing parameters
- Output formatting options

## Output

The pipeline generates a `seller_performance_report.json` file containing:
- Seller performance metrics
- Sales analytics
- Product performance data