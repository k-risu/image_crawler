# 구글 이미지 크롤링 웹드라이버 - 웹드라이버 설정 / last update : 20250521
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from .config import CHROME_OPTIONS

def setup_webdriver():
    """웹드라이버 설정을 초기화하고 반환하는 함수"""
    chrome_options = Options()
    for option in CHROME_OPTIONS:
        chrome_options.add_argument(option)
    
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # ChromeDriverManager를 사용하여 드라이버 자동 설치 및 관리
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(3)
    
    return driver, WebDriverWait(driver, 2) 