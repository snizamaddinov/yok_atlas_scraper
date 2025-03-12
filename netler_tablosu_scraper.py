from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from time import sleep
from bs4 import BeautifulSoup
from typing import List
from selenium.webdriver.remote.webelement import WebElement
import re
import csv
import json
import os
from dotenv import dotenv_values
import enum
import json
import time
import requests

class BaseScraper:
    class ProgramType(enum.Enum):
        SAY = 'SAY'
        SOZ = 'SÖZ'
        EA = 'EA'
        DIL = 'DİL'
        TYT = 'TYT'

    BASE_DOMAIN = 'https://yokatlas.yok.gov.tr'

    def __init__(self, file_name):
        self.base_domain = self.BASE_DOMAIN
        self.file_name = file_name
        self.driver = None
        self.compiled_patterns = {
            'apostrophe': re.compile(r"[\u2019\u2018\u2032\u0060\u00B4\u02BC\u02BB\u02BD\u0022\u201C\u201D\u201E\u2033\u2036\u275D]"),
            'whitespace': re.compile(r"[\n\r\t]"),
            'multiple_spaces': re.compile(r"\s{2,}"),
            'decimal_point': re.compile(r"^-?\d+,\d+$"),
            'integer_number': re.compile(r"^-?\d+$")
        }

        self.all_key_index_map = {
            "program_kodu": -1,
            "program_adi": -1,
            "program_turu": -1,
            "universite_kodu": -1,
            "universite": 0,
            "yil": 1,
            "tur": 2,
            "katsayi": 3,
            "yerlesen_son_kisi": 4,
            "yerlesen": 5,
            "tyt_turkce": 6,
            "tyt_sosyal": 7,
            "tyt_matematik": 8,
            "tyt_fen": 9,
            "ayt_matematik": -1,
            "ayt_fizik": -1,
            "ayt_kimya": -1,
            "ayt_biyoloji": -1,
            "ayt_turkce": -1,
            "ayt_tar1": -1,
            "ayt_cog1": -1,
            "ayt_tar2": -1,
            "ayt_cog2": -1,
            "ayt_fel": -1,
            "ayt_din": -1,
            "ydt_dil": -1

        }

        self.type_key_index_map = {
            BaseScraper.ProgramType.SAY.value: {
                'ayt_matematik': 10,
                'ayt_fizik': 11,
                'ayt_kimya': 12,
                'ayt_biyoloji': 13
            },

            BaseScraper.ProgramType.SOZ.value: {
                'ayt_turkce': 10,
                'ayt_tar1': 11,
                'ayt_cog1': 12,
                'ayt_tar2': 13,
                'ayt_cog2': 14,
                'ayt_fel': 15,
                'ayt_din': 16

            },

            BaseScraper.ProgramType.EA.value: {
                'ayt_matematik': 10,
                'ayt_turkce': 11,
                'ayt_tar1': 12,
                'ayt_cog1': 13
            },

            BaseScraper.ProgramType.DIL.value: {
                'ydt_dil': 10
            },

            BaseScraper.ProgramType.TYT.value: {
            }

        }

    def get_options(self):
        options = webdriver.ChromeOptions()
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,tr;q=0.8,ru;q=0.7",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        for key, value in headers.items():
            options.add_argument(f"--{key}={value}")
        return options

    def start_driver(self):
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=self.get_options())

    def stop_driver(self):
        if self.driver:
            self.driver.quit()

    def load_page(self, path, timeout=5):
        url = f"{self.base_domain}{path}"
        try:
            self.driver.get(url)
            element_present = EC.presence_of_element_located((By.CSS_SELECTOR, 'table#mydata'))
            WebDriverWait(self.driver, timeout).until(element_present)
            sleep(1)

        except Exception as e:
            print(e)
            print(f'Error loading page: {url}')

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = self.compiled_patterns['apostrophe'].sub("'", text)
        text = self.compiled_patterns['whitespace'].sub(" ", text)
        text = self.compiled_patterns['multiple_spaces'].sub(" ", text)

        return text.strip()

    def convert_comma_floats(self, data):
        def try_convert(value):
            if isinstance(value, str):
                if re.match(self.compiled_patterns['decimal_point'], value):  
                    return float(value.replace(',', '.'))
                elif re.match(self.compiled_patterns['integer_number'], value):  # Handle integer-like strings
                    return int(value)

            return value

        return [{k: try_convert(v) for k, v in item.items()} for item in data]

    def get_university_codes(self, table_body)-> list[str]:
        rows = table_body.select('tbody tr')
        codes = []
        for row in rows:
            cols = row.select('td')
            code = ''
            if cols and len(cols) > 0:
                uni_col = cols[1]
                a_tag = uni_col.find('a')
                if a_tag:
                    href = a_tag['href']
                    code = href.split('=')[-1]
                    code = self.clean_text(code)

            codes.append(code)
        
        # exit()
        return codes

    def get_table_body(self, soup):
        try:
            table_body = soup.find('tbody')
            if not table_body:
                return []

            rows = [
                [ self.clean_text(td.get_text()) for td in row.select('td')[1:] ]
                for row in table_body.select('tr')
            ]
            return rows

        except Exception as e:
            print(f'Error extracting table body: {e}')
            return []
        
    def get_program_type(self):
        h2_elements: List[WebElement] = self.driver.find_elements(By.CSS_SELECTOR, 'h2')

        h2_elements: BeautifulSoup = [BeautifulSoup(h2.get_attribute('outerHTML'), 'lxml') for h2 in h2_elements]

        for h2 in h2_elements:
            strong_text = h2.find('strong')
            if strong_text and strong_text.get_text():
                strong_text = strong_text.get_text().lower()
                for program_type in self.ProgramType:
                    formatted_program_type = f"({program_type.value})".lower()
                    if formatted_program_type in strong_text:
                        return program_type.value

        return self.ProgramType.SAY.value # default

    def scrape_page(self, program_id, program_name):
        print(f"Scraping program: {program_name}")
        print(f"Program ID: {program_id}")
        try:
            program_type = self.get_program_type()

            key_index_map = self.all_key_index_map.copy()
            key_index_map.update(self.type_key_index_map.get(program_type, {}))
            json_values = []

            while True:
                table = self.driver.find_element(By.ID, 'mydata')
                table_html = table.get_attribute('outerHTML')
                table_soup = BeautifulSoup(table_html, 'lxml')

                row_list = self.get_table_body(table_soup)
                if len(row_list) == 0 or len(row_list[0]) < 9:
                    break


                uni_codes = self.get_university_codes(table_soup)

                for uni_code, row in zip(uni_codes, row_list):
                    value = {}
                    for k, v in key_index_map.items():
                        if v != -1:
                            value[k] = row[v]
                        else:
                            value[k] = ''

                    value['universite_kodu'] = uni_code
                    value['program_kodu'] = program_id
                    value['program_adi'] = program_name
                    value['program_turu'] = program_type

                    json_values.append(value)

                next_button = self.driver.find_element(By.ID, 'mydata_next')
                if 'disabled' in next_button.get_attribute('class'):
                    break
                else:
                    try:
                        next_button_link = next_button.find_element(By.TAG_NAME, 'a')
                        if next_button_link:
                            self.driver.execute_script("arguments[0].scrollIntoView();", next_button_link)
                            self.driver.execute_script("document.querySelector('.well.well-sm').style.display='none';")
                            sleep(1)
                            self.driver.execute_script("arguments[0].click();", next_button_link)
                            sleep(3)
                    except Exception as e:
                        print("ERROR clicking next button: ", e)
                        print("Error while scraping page")
                        print(f"Program ID: {program_id}")
                        print(f"Program Name: {program_name}")
                        break
    
            json_values = self.convert_comma_floats(json_values)
            return json_values
        
        except Exception as e:
            print(e)
            print('ERROR in scrape_page method')
            print(f"Program ID: {program_id}")
            print(f"Program Name: {program_name}")
            return []

    def save_to_csv(self, headers, body):
        try:
            with open(self.file_name, 'a+', newline='', encoding='utf-8-sig') as file:
                file.seek(0)
                writer = csv.writer(file)
                if not file.readline().strip():
                    writer.writerow(headers)
                for row in body:
                    writer.writerow(row)
        except Exception as e:
            print(e)
            print('Error while saving to csv')

    def append_to_json(self, body):
        if not body:
            return
        
        if not os.path.exists(self.file_name):
            with open(self.file_name, 'w', encoding='utf-8') as f:
                json.dump(body, f, ensure_ascii=False)
            return
        
        with open(self.file_name, 'rb+') as f:
            f.seek(0, os.SEEK_END)
            pos = f.tell() - 1
            while pos > 0:
                f.seek(pos)
                if f.read(1) not in b' \n\r\t':
                    break
                pos -= 1

            f.seek(pos)
            last_char = f.read(1)
            if last_char != b']':
                raise ValueError("Invalid JSON file format: does not end with a closing bracket")
            f.seek(pos)
            f.truncate()
            if pos > 1:
                f.seek(pos - 1)
                if f.read(1) not in b'[':
                    f.write(b',')
            f.write(json.dumps(body, ensure_ascii=False)[1:-1].encode('utf-8'))
            f.write(b']')

    def scrape_programs(self, path :str, programs: list[dict]):
        self.start_driver()
        formatted_path = path if path.startswith('/') else f'/{path}'

        try:
            for program in programs:
                if not program['id']:
                    continue
                try:
                    final_path = formatted_path + f"?b={program['id']}"
                    self.load_page(final_path)
                    sleep(3)
                    select_element = self.driver.find_element(By.NAME, 'mydata_length')
                    if select_element:
                        Select(select_element).select_by_value('100')
                        sleep(2)

                    json_values = self.scrape_page(program_id=program['id'], program_name=program['name'])
                    self.append_to_json(json_values)

                except TimeoutException:
                    print(f"Timeout while scraping: {self.base_domain}{path}")
                except Exception as e:
                    print(e)
                    print(f'Error processing: {self.base_domain}{path}')
        finally:
            self.stop_driver()


    def get_initial_page(self, css_id):
        url = f"{self.base_domain}/netler.php"

        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'lxml')
        select = soup.find('select', {'id': css_id})
        options = select.find_all('option')
        
        scraped_options = []
        for option in options:
            value = option['value']
            text = self.clean_text(option.get_text())
            if value and text:
                scraped_options.append({
                    'id': value,
                    'name': text
                })
        return scraped_options


class BachelorScraper(BaseScraper):
    FILE_NAME_PREFIX = 'bachelor_data'
    PATH = '/netler-tablo.php'

    def __init__(self):
        formatted_time = time.strftime("%Y%m%d_%H%M")
        file_name = f"{self.FILE_NAME_PREFIX}_{formatted_time}.json"
        super().__init__(file_name)


    def scrape(self):
        bolumler = self.get_initial_page('bolum')
        # bolumler = [
        #     {
        #         'id': '10206',
        #         'name': 'Bilgisayar Mühendisliği'
        #     }
        # ]
        self.scrape_programs(path=self.PATH, programs=bolumler[10:])


class AssociateScraper(BaseScraper):
    FILE_NAME_PREFIX = 'associate_data'
    PATH = '/netler-onlisans-tablo.php'

    def __init__(self):
        formatted_time = time.strftime("%Y%m%d_%H%M")
        file_name = f"{self.FILE_NAME_PREFIX}_{formatted_time}.json"
        super().__init__(file_name)

    def scrape(self):
        programs = self.get_initial_page('program')
        self.scrape_programs(path=self.PATH, programs=programs)

if __name__ == '__main__':
    print("Starting BachelorScraper")
    BachelorScraper().scrape()
    print("Starting AssociateScraper")
    AssociateScraper().scrape()