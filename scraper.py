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

base_url = 'https://yokatlas.yok.gov.tr/tercih-sihirbazi-t4-tablo.php?p=say'

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


def get_table_header(table_header):
    if table_header:
        header_cells = table_header.find_all('th')
        headers = []
        for cell in header_cells:
            cell_text = ''.join(cell.find_all(string=True, recursive=False)).strip().rstrip('*')

            if cell_text:
                headers.append(cell_text)
        # print(headers)
        return headers


def scrape_page(driver, headers, body):

    def is_valid_text(text):
        return re.search(r'\w', text)
    
    def get_clean_text(text_arr):
        for text in text_arr:
            if(text):
                return text.strip().rstrip('*')

    try:
        table = driver.find_element(By.ID, 'mydata')
        outer_html = table.get_attribute('outerHTML')
        soup = BeautifulSoup(outer_html, 'html.parser')

        if not headers:
            table_head = soup.find('thead')
            headers.extend(get_table_header(table_head))

        table_body = soup.find('tbody')
        scraped_rows = []
        columns = []
        if table_body:
            rows = table_body.find_all('tr')
            for row in rows[:2]:
                cells = row.find_all('td')
                for cell in cells:
                    text_candidates = cell.find_all(string=is_valid_text, recursive=True)
                    cell_text = get_clean_text(text_candidates)
                    if cell_text:
                        if '+' in cell_text:
                            cell_text = str(sum(int(number) for number in cell_text.split('+')))
                        
                        columns.append(cell_text)
                scraped_rows.append(columns)

        body.extend(scraped_rows)
    except Exception as e: 
        print(e)
        print('Error while scraping page')
    

def main():
    headers = []
    service = Service()
    options = get_options()
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(base_url)
    timeout = 5


    try:
        element_present = EC.presence_of_element_located((By.ID, 'mydata_processing'))
        WebDriverWait(driver, timeout).until(element_present)

        select_element = driver.find_element(By.NAME, 'mydata_length')
    
        # Wrap the select element in Select class
        select = Select(select_element)
        
        # Select 100 entries per page
        select.select_by_value('100')
        sleep(1)
        count = 0
        body = []
        while (count := count + 1) < 3:
            scrape_page(driver, headers, body)

            next_button = driver.find_element(By.ID, 'mydata_next')

            if 'disabled' in next_button.get_attribute('class'):
                break
            else:
                next_button.click()
                sleep(1)
                print("Clicked on 'Sonraki' for the next page")

        print("AFTER SCRAPE: ")
        print(headers)
        print(body)
    except TimeoutException:
        print("Timed out waiting for page to load")
    finally:
        sleep(4)
        driver.quit()


if __name__ == '__main__':
    main()

    # print(driver_path)
