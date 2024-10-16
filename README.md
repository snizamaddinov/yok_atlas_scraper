# Scraper

## Description

This project uses Selenium and BeautifulSoup to scrape data from a list of URLs. The URLs and the output filename are specified in an environment file.

## Requirements

To run this project, you will need the following software:

- Python 3.6 or later: 

- Google Chrome 119: The version should be compatible with the ChromeDriver version.

## Installation

To install the necessary requirements, run the following command in your terminal:

```
    pip install -r requirements.txt
```

## Usage
Before running the script, make sure to set up your environment file with the following variables:

* URLS: A list of URLs to scrape.
* FILENAME: The name of the file where the scraped data will be saved.

Once your environment file is set up, you can run the script with the following command:

```
python script.py
```