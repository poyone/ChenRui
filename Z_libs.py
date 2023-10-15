import json
import pprint
import random
import re
from datetime import datetime, timedelta


import requests
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DriverInitialize:
    
    def __init__(self, profile_path, login_site) -> None:
        
        webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

        options = Options()
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        options.add_argument(f'--user-data-dir={profile_path}')
        # options.binary_location = driver_path
        options.add_argument('--log-level=3')

        self.driver = webdriver.Chrome(options=options)
        self.driver.get(login_site)
        self.driver.implicitly_wait(10)
    
    def reserved_operation(self):
        pass
    
    def quit_browser(self):

        return self.driver

class SessionInteractor:
    
    def __init__(self, driver: webdriver):
        self.session = requests.Session()
        for cookie in driver.get_cookies():
            self.session.cookies.set(cookie['name'], cookie['value'])

    def return_session(self):
        return self.session
    
def removeBlank(string: str):
    
    return(re.sub(re.compile(r'\s+',re.S),'',string))

def format_date(days_ago: str):

    formatted_date = datetime.strftime(datetime.fromtimestamp(int(days_ago)), '%Y-%m-%d %H:%M:%S')
    
    return formatted_date