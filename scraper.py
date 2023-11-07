from selenium import webdriver
from selenium.webdriver.chrome.service import Service   
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from time import sleep
from bs4 import BeautifulSoup
import re
import csv
from dotenv import dotenv_values
import json
import os


def get_table_header(soup):
    def get_clean_header_text(cell):
        return ''.join(cell.find_all(string=True, recursive=False)).strip().rstrip('*')

    try:
        table_header = soup.find('thead')
        if table_header:
            header_cells = table_header.find_all('th')
            headers = [get_clean_header_text(cell) for cell in header_cells if get_clean_header_text(cell)]

            return headers

    except Exception as e:
        print(e)
        print('Error while scraping table header')


def get_table_body(soup):
    def is_valid_text(text):
        return re.search(r'\w', text)

    def get_clean_text(text_arr):
        for text in text_arr:
            if text:
                return text.strip().rstrip('*').rstrip('-')

    def get_cell_texts(row):
        result = []
        for cell in row.find_all('td'):
            red_class_element = cell.find(attrs={'color': 'red'})
            if red_class_element:
                result.append(get_clean_text( [ red_class_element.get_text().strip().rstrip('*').rstrip('-') ] ) )
            else:
                result.append(get_clean_text(cell.find_all(string=is_valid_text, recursive=True)))

        return result

    def process_cell_text(cell_text):
        result = [cell_text]

        if not cell_text:
            result = ['']

        elif re.search(r'.*\-[0-9]+$', cell_text):
            result = cell_text.split('-')
        
        elif '+' in cell_text:
            result = [ str(sum(int(number) for number in cell_text.split('+'))) ]

        return result
    
    try:
        table_body = soup.find('tbody')
        
        if table_body:
            rows = table_body.find_all('tr')
            scraped_rows = []

            for row in rows:
                # print(row)
                cells = get_cell_texts(row)
                # print(cells)
                columns = [cell_text for cell in cells
                           for cell_text in process_cell_text(cell)]
                # print(columns)
                if not columns[0]:
                    del columns[0]
                scraped_rows.append(columns)

            return scraped_rows
    except Exception as e:
        print(e)
        print('Error while scraping table body')


def scrape_page(driver):
    try:
        table = driver.find_element(By.ID, 'mydata')
        outer_html = table.get_attribute('outerHTML')
        soup = BeautifulSoup(outer_html, 'html.parser')

        header = get_table_header(soup)

        body = []
        while True:
            body += get_table_body(soup)

            next_button = driver.find_element(By.ID, 'mydata_next')
            if 'disabled' in next_button.get_attribute('class'):
                break
            else:
                next_button.click()
                sleep(1)

                # print("Clicked on 'Sonraki' for the next page")
                table = driver.find_element(By.ID, 'mydata')
                outer_html = table.get_attribute('outerHTML')
                soup = BeautifulSoup(outer_html, 'html.parser')

        return header, body

    except Exception as e: 
        print(e)
        print('Error while scraping page')


def save_to_csv(headers, body, file_name):
    try:
        with open(file_name, 'a+', newline='', encoding='utf-8-sig') as file:
            file.seek(0)
            header = file.readline()
            header = header.strip()

            writer = csv.writer(file)
            if not header or len(header) < 10:
                writer.writerow(headers)
            
            file.seek(0, os.SEEK_END)

            # Append new rows
            for row in body:
                writer.writerow(row)

    except Exception as e:
        print(e)
        print('Error while saving to csv')


def get_options():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,tr;q=0.8,ru;q=0.7",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "_ga=GA1.3.707879593.1699213628; _gid=GA1.3.1976060829.1699213628; _gat=1; _ga_V5NGP2K979=GS1.3.1699213628.1.0.1699213628.0.0.0",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"'
    }

    for key, value in headers.items():
        options.add_argument(f"--{key}={value}")

    return options


def load_page(driver, url, timeout=5):
    driver.get(url)
    element_present = EC.presence_of_element_located((By.ID, 'mydata_processing'))
    WebDriverWait(driver, timeout).until(element_present)
    sleep(1)


def main():
    config = dotenv_values(".env")
    service = Service()
    options = get_options()
    urls = json.loads(config['URLS'])
    file_name = config['FILE_NAME']
    # exit()

    with webdriver.Chrome(service=service, options=options) as driver:
       for url in urls:
            try:
                load_page(driver, url)

                select_element = driver.find_element(By.NAME, 'mydata_length')
                select = Select(select_element)
                select.select_by_value('100')
                sleep(1)
                
                headers, body = scrape_page(driver)

                if 'p=tyt' in url:
                    for row in body: 
                        row[-1], row[-2] = row[-2], row[-1]

                save_to_csv(headers, body, file_name)

                print("SCRAPED: ", url)

            except TimeoutException:
                print("Timed out waiting for page to load")

            except StopIteration:
                print("Finished scraping")

            except Exception as e:
                print(e)
                print('Error while scraping')


if __name__ == '__main__':
    main()
