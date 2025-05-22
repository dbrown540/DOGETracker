# DOGE Tracker

A Python-based tool for tracking and analyzing DOGE (Defense of Government Efficiency) savings data from government contracts.

## Project Overview

This project scrapes and processes DOGE savings data from government contracts, providing insights into cost savings and contract modifications.

## Architecture

```mermaid
graph TD
    A[Web Scraper] --> B[Data Processor]
    B --> C[Data Exporter]
    C --> D[CSV Files]
    
    subgraph Components
        A
        B
        C
        D
    end
```

## Data Flow

```mermaid
sequenceDiagram
    participant S as Scraper
    participant P as Processor
    participant E as Exporter
    participant D as Data Store
    
    S->>P: Raw Contract Data
    P->>E: Processed Data
    E->>D: CSV Export
```

## Project Structure

```mermaid
graph TD
    A[src/] --> B[scrapers/]
    A --> C[processors/]
    A --> D[exporters/]
    A --> E[utils/]
    A --> F[models/]
    A --> G[webdriver/]
    A --> H[parsers/]
```

## Dependencies

- Python 3.x
- selenium==4.31
- requests==2.32.3
- pandas
- BeautifulSoup4
- coloredlogs==15.0.1

## Configuration

The project uses a `settings.py` file for configuration, including:
- API endpoints
- Retry settings
- Data field mappings
- File paths

## Data Fields

The system tracks the following fields for each contract:
- PIID (Procurement Instrument Identifier)
- Agency
- Vendor
- Value
- Description
- FPDS Status
- FPDS Link
- Deleted Date
- Savings

## Getting Started

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the main script:
   ```bash
   python src/main.py
   ```

## Data Storage

Processed data is stored in CSV format in the `data/` directory, with raw API data saved to `data/doge_raw_api_data.csv`. 