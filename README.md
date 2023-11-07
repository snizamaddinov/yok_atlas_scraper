# Scraper

## Description

This project uses Selenium and BeautifulSoup to scrape data from a list of URLs. The URLs and the output filename are specified in an environment file.

## Requirements

To run this project, you will need the following software:

- Python 3.6 or later: 

- Google Chrome 119: The version should be compatible with the ChromeDriver version.

- ChromeDriver 119: 
 

## Installation

To install the necessary requirements, run the following command in your terminal:

```
    pip install -r requirements.txt
```


Download the ChromeDriver from the following link:

[ChromeDriver Download](https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/mac-x64/chromedriver-mac-x64.zip)

The downloaded version of ChromeDriver is 119.0.6045.105, which is compatible with Chrome version 119. Make sure to install the compatible version of Chrome.

For the next steps, you might want to:

* Check if the ChromeDriver version is still compatible with your current version of Chrome.

* If not, download the appropriate version of ChromeDriver.
Make sure that ChromeDriver is correctly installed and added to your system's PATH.

## Usage
Before running the script, make sure to set up your environment file with the following variables:

* URLS: A list of URLs to scrape.
* FILENAME: The name of the file where the scraped data will be saved.

Once your environment file is set up, you can run the script with the following command:

```
python script.py
```