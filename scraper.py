from selenium import webdriver
from selenium.webdriver.chrome.service import Service   
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from time import sleep

base_url = 'https://yokatlas.yok.gov.tr/tercih-sihirbazi-t4-tablo.php?p=say'

def get_options():
    options = webdriver.ChromeOptions()
    # Add the desired headers
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,tr;q=0.8,ru;q=0.7",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "_ga=GA1.3.707879593.1699213628; _gid=GA1.3.1976060829.1699213628; _gat=1; _ga_V5NGP2K979=GS1.3.1699213628.1.0.1699213628.0.0.0",
        # Add other headers here
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"'
    }

    for key, value in headers.items():
        options.add_argument(f"--{key}={value}")

    return options

def main():
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
        print("Selected 100 entries per page")
        sleep(1)
        
        next_button = driver.find_element(By.ID, 'mydata_next')

        if 'disabled' not in next_button.get_attribute('class'):
            next_button.click()
            print("Clicked on 'Sonraki' for the next page")
        else:
            print("Already on the last page. 'Sonraki' button is disabled.")

    except TimeoutException:
        print("Timed out waiting for page to load")
    finally:
        print("Page loaded")
        sleep(10)
        driver.quit()


if __name__ == '__main__':
    main()

    # print(driver_path)
