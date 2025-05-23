# 구글 이미지 크롤링 프로세서 - 이미지 처리 및 추출 / last update : 20250521

import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import unquote
from .config import IMAGE_SELECTORS, BIG_IMAGE_SELECTORS, LINK_SELECTORS
import time

def find_link_in_container(container, i):
    # 이미지 컨테이너에서 링크를 찾는 함수
    for selector in LINK_SELECTORS:
        try:
            link_element = container.find_element(By.CSS_SELECTOR, selector)
            if link_element:
                href = link_element.get_attribute('href')
                if href:
                    logging.info(f"{i}번째 이미지의 사이트 URL 발견: {href}")
                    return href
        except:
            continue
    return None

def find_image_element(container, current_image_index):
    # 컨테이너 내의 이미지 요소를 찾는 함수
    for selector in IMAGE_SELECTORS:
        try:
            img = container.find_element(By.CSS_SELECTOR, selector)
            if img:
                logging.info(f"{current_image_index}번째 이미지 찾음 (선택자: {selector})")
                return img
        except:
            continue
    return None

def find_big_image(driver, wait, current_image_index):
    # 큰 이미지를 찾는 함수
    for selector in BIG_IMAGE_SELECTORS:
        try:
            big_img = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            if big_img:
                # TIA 이미지 클래스 확인
                img_class = big_img.get_attribute('class')
                if img_class and 'yAnw3c' in img_class:
                    logging.info(f"{current_image_index}번째 이미지 건너뜀 (TIA 이미지 클래스): {img_class}")
                    continue
                
                logging.info(f"{current_image_index}번째 이미지 선택자 매칭: {selector}")
                return big_img
        except:
            continue
    return None

def process_image_url(big_img, current_image_index, collected_site_urls, driver):
    # 이미지 URL을 처리하는 함수
    이미지_url = big_img.get_attribute('src')
    if not 이미지_url:
        이미지_url = big_img.get_attribute('data-src')
    
    if 이미지_url:
        # URL 디코딩
        이미지_url = unquote(이미지_url)
        
        # 구글 TIA 이미지 필터링
        if 'google.com/tia' in 이미지_url.lower():
            logging.info(f"{current_image_index}번째 이미지 건너뜀 (TIA 이미지): {이미지_url}")
            return None
        
        # 웹페이지 URL인 경우 처리
        if not any(ext in 이미지_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            # 현재 이미지가 Instagram 링크인지 확인
            is_instagram = False
            for idx, url in collected_site_urls:
                if idx == current_image_index and 'instagram.com' in url.lower():
                    is_instagram = True
                    break
            
            if is_instagram:
                # Instagram 링크인 경우 현재 방식으로 처리
                href = None
                for idx, url in collected_site_urls:
                    if idx == current_image_index:
                        href = url
                        break
                
                if href:
                    logging.info(f"{current_image_index}번째 URL이 Instagram URL입니다. 이미지 추출 시도: {href}")
                    
                    # 새 탭에서 웹페이지 열기
                    driver.execute_script(f"window.open('{href}', '_blank');")
                    time.sleep(2)
                    
                    # 새 탭으로 전환
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(3)
                    
                    try:
                        # 모든 이미지 요소 찾기
                        all_images = driver.find_elements(By.TAG_NAME, "img")
                        for img in all_images:
                            try:
                                src = img.get_attribute('src')
                                if src and not 'encrypted-tbn0.gstatic.com' in src:
                                    # 이미지 크기 확인
                                    width = img.get_attribute('width')
                                    height = img.get_attribute('height')
                                    if width and height:
                                        w = int(width)
                                        h = int(height)
                                        if w > 200 and h > 200:
                                            이미지_url = src
                                            logging.info(f"{current_image_index}번째 웹페이지에서 이미지 URL 추출: {이미지_url}")
                                            break
                            except:
                                continue
                        
                        # 새 탭 닫기
                        driver.close()
                        # 원래 탭으로 돌아가기
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(1)
                    except Exception as e:
                        logging.error(f"{current_image_index}번째 웹페이지 이미지 URL 추출 실패: {str(e)}")
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(1)
                        return None
                else:
                    logging.error(f"{current_image_index}번째 이미지의 링크를 찾을 수 없습니다.")
                    return None
            else:
                # Instagram이 아닌 경우 이전 방식 사용
                try:
                    parent_a = big_img.find_element(By.XPATH, "./ancestor::a")
                    if parent_a:
                        href = parent_a.get_attribute('href')
                        if href:
                            logging.info(f"{current_image_index}번째 이미지의 실제 링크 발견: {href}")
                except Exception as e:
                    logging.error(f"{current_image_index}번째 이미지의 링크 추출 실패: {str(e)}")
                    return None
        
        # 실제 이미지 URL인지 확인
        if not any(ext in 이미지_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            logging.info(f"{current_image_index}번째 이미지 건너뜀 (이미지 확장자 없음): {이미지_url}")
            return None
        
        logging.info(f"{current_image_index}번째 이미지 URL 수집 완료: {이미지_url}")
        return 이미지_url
    
    return None 