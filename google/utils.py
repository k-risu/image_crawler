# 구글 이미지 크롤링 유틸리티 - 이미지 확장자 처리 및 다운로드 / last update : 20250521

import os
import mimetypes
import logging
from urllib.parse import urlparse, unquote
import requests
from .config import EXCLUDED_URL_PATTERNS

def get_image_extension(url, content_type=None):
    """이미지 URL과 Content-Type을 기반으로 확장자를 결정"""
    parsed = urlparse(url)
    path = parsed.path
    ext = os.path.splitext(path)[1].lower()
    
    if not ext and content_type:
        ext = mimetypes.guess_extension(content_type)
    
    if not ext:
        ext = '.jpg'
    
    return ext

def download_image(args):
    """개별 이미지 다운로드를 처리하는 함수"""
    i, 이미지_url, 다운로드_폴더 = args
    try:
        # 구글 TIA 이미지 및 기타 불필요한 이미지 필터링
        if any(x in 이미지_url.lower() for x in EXCLUDED_URL_PATTERNS):
            logging.info(f"{i}번 이미지 건너뜀 (필터링된 URL): {이미지_url}")
            return False

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.google.com/'
        }
        
        response = requests.get(이미지_url, headers=headers, timeout=3)
        if response.status_code == 200:
            # 이미지 크기 확인 (너무 작은 이미지 제외)
            content_length = len(response.content)
            if content_length < 10000:  # 10KB 미만의 이미지는 제외
                logging.info(f"{i}번 이미지 건너뜀 (파일 크기 너무 작음): {content_length} bytes")
                return False

            ext = get_image_extension(이미지_url, response.headers.get('content-type'))
            파일명 = os.path.join(다운로드_폴더, f'image_{i}{ext}')
            with open(파일명, 'wb') as f:
                f.write(response.content)
            logging.info(f"{i}번 이미지 다운로드 성공: {파일명}")
            return True
        else:
            logging.error(f"{i}번 이미지 다운로드 실패. 상태 코드: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"{i}번 이미지 다운로드 실패: {str(e)}")
        return False 