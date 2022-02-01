from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import argparse
import time
import json

from notify import notify

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--update-time', '-t', default=10, required=False, type=int, help='Interval time for each update in seconds')
    parser.add_argument('--dry', '-d', type=int, help='Case value for dry run (default 25)', required=False)
    parser.add_argument('--headless', '-hd', help='Run selenium chromedriver in headless mode', default=False, action='store_true')
    parser.add_argument('--credentials', '-c', type=str, help='Path to JSON credential file (with fields "username" and "password")')
    args = parser.parse_args()

    try:
        op = webdriver.ChromeOptions()
        if args.headless:
            op.add_argument('headless')
        driver = webdriver.Chrome(options=op)
        driver.get('https://www.jisedu.or.id/student')
        
        if args.credentials:
            with open(args.credentials, 'r') as f:
                credentials = json.load(f)
            
            if 'username' not in credentials.keys():
                raise Exception('Field "username" not in credentials file')

            if 'password' not in credentials.keys():
                raise Exception('Field "password" not in credentials file')

            username_input = driver.find_element_by_id('fsLoginUsernameField1144')
            username_input.send_keys(credentials['username'])

            password_input = driver.find_element_by_id('fsLoginPasswordField1144')
            password_input.send_keys(credentials['password'])
            
            submit = driver.find_element_by_css_selector(".fsLoginSubmit[value='Login']")
            submit.click()
        else:
            login = input('Please login (click enter once you are done)')
        
        try:
            hide_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'fsPagePopHideButton'))
            )
            hide_button.click()
        except TimeoutException:
            pass

        def get_cases():
            cases = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div/main/div/div/div[2]/div[2]/div[1]/div/p[2]'))
            ).text
            return int(cases.replace('Number of Active Cases: ', '').strip())

        cases = args.dry or get_cases()
        notify('Jisnet Covid Tracker', f'Successfully started at {cases} cases')

        while True:
            new_cases = get_cases()
            if new_cases != cases:
                num_new = new_cases - cases
                print('cases updated!')
                notify('JIS CASES UPDATE', f'{num_new} new cases, total {new_cases}')
            
            cases = new_cases

            time.sleep(args.update_time)
            driver.refresh()

    finally:
        driver.quit()
