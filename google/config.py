# 구글 이미지 크롤링 설정 - 설정 파일 / last update : 20250521

import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('image_download.log'),
        logging.StreamHandler()
    ]
)

# Chrome 옵션 설정
CHROME_OPTIONS = [
    '--headless',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--window-size=1920,1080',
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    '--disable-blink-features=AutomationControlled',
    '--disable-extensions',
    '--disable-logging',
    '--disable-notifications',
    '--disable-infobars',
    '--disable-popup-blocking',
    '--disable-save-password-bubble',
    '--disable-translate',
    '--disable-web-security',
    '--disable-features=IsolateOrigins,site-per-process'
]

# 이미지 필터링을 위한 제외 URL 패턴
EXCLUDED_URL_PATTERNS = [
    'google.com/tia',
    'gstatic.com',
    'googleusercontent.com/icon',
    'google.com/images/icons',
    'google.com/images/branding',
    'google.com/images/cleardot.gif',
    'google.com/images/nav_logo'
]

# 이미지 선택자 목록
IMAGE_SELECTORS = [
    "img.YQ4gaf",
    "img[jsname='kn3ccd']",
    "img[jsname='JuXqh']",
    "img.sFlh5c",
    "img"
]

# 큰 이미지 선택자 목록
BIG_IMAGE_SELECTORS = [
    "img[jsname='kn3ccd']",
    "img[jsname='JuXqh']",
    "img.n3VNCb",
    "img.sFlh5c"
]

# 링크 선택자 목록
LINK_SELECTORS = [
    "a.YsLeY",
    "a[jsaction*='trigger.HTIQtd']",
    "a[role='link']",
    "a[data-ved]",
    "a[href*='instagram.com']",
    "a[href*='kmong.com']",
    "a"
] 