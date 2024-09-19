# Dive Shop Data Scraper

This script will download all the dive shops visible through the PADI.com site.

## Description

The Dive Shop Data Scraper fetches data about dive shops from the PADI website, including their details and contact information. The data is saved in both JSON and optionally in Excel format.

## Features

- Fetches dive shop data from the PADI API.
- Extracts email addresses using a decoding algorithm.
- Saves the data in JSON format.
- Optionally saves the data in Excel format.

## Requirements

- Python 3.x
- `requests` library
- `pandas` library
- `BeautifulSoup` from `bs4`

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/dive-shop-scraper.git
   cd dive-shop-scraper
   ```

2. Create and activate a virtual environment:
    ```bash
    python t-m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. Install the required packages:
    ```bash
    pip install requests pandas beautifulsoup4 openpyxl
    ```

## Usage