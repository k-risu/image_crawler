# 구글 이미지 크롤링 다운로드 - 이미지 다운로드 / last update : 20250521
import os
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
from .web_driver import setup_webdriver
from .image_processor import find_link_in_container, find_image_element, find_big_image, process_image_url
from .utils import download_image

def image_download(url, class_names, download_count=10, save_location=None, button_frame=None):
    logging.info(f"이미지 다운로드 시작: {url}, 다운로드 개수: {download_count}")
    
    # 사이트 URL 리스트를 저장할 리스트 추가
    collected_site_urls = []
    
    # 웹드라이버 설정
    driver, wait = setup_webdriver()
    
    try:
        # 웹페이지 로드
        logging.info("구글 이미지 검색 페이지 로딩 중...")
        driver.get(url)
        
        # 페이지 로딩을 위한 최소 대기
        time.sleep(0.3)
        
        logging.info("페이지 로딩 완료, 이미지 찾는 중...")
        
        try:
            # 다운로드 폴더 생성
            if save_location is None:
                save_location = '다운로드된_이미지'
            if not os.path.exists(save_location):
                os.makedirs(save_location)
                logging.info(f"다운로드 폴더 생성: {save_location}")
            
            # 이미지 컨테이너 찾기
            image_containers = driver.find_elements(By.CSS_SELECTOR, "div.eA0Zlc")
            
            if image_containers:
                logging.info(f"이미지 컨테이너를 찾았습니다. 개수: {len(image_containers)}")
                
                # 먼저 모든 이미지의 사이트 URL 수집
                for i, container in enumerate(image_containers[:download_count], 1):
                    if button_frame and button_frame.is_cancelled:
                        logging.info("검색이 취소되어 URL 수집을 중단합니다.")
                        return
                    try:
                        href = find_link_in_container(container, i)
                        if href:
                            collected_site_urls.append((i, href))
                    except Exception as e:
                        logging.error(f"{i}번째 이미지의 사이트 URL을 찾을 수 없습니다: {str(e)}")
                
                # ThreadPoolExecutor 생성
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = []
                    
                    # 다운로드할 이미지 개수만큼 반복
                    for i in range(min(download_count, len(image_containers))):
                        if button_frame and button_frame.is_cancelled:
                            logging.info("검색이 취소되어 이미지 다운로드를 중단합니다.")
                            # 실행 중인 모든 작업 취소
                            for future in futures:
                                future.cancel()
                            break
                            
                        try:
                            # 이미지 컨테이너 선택
                            container = image_containers[i]
                            current_image_index = i + 1
                            
                            # 컨테이너 내의 이미지 찾기
                            img = find_image_element(container, current_image_index)
                            if not img:
                                logging.error(f"{current_image_index}번째 이미지를 찾을 수 없습니다.")
                                continue
                            
                            # 이미지 클릭
                            logging.info(f"{current_image_index}번째 이미지 클릭 시도 중...")
                            driver.execute_script("arguments[0].click();", img)
                            
                            # 클릭 후 동적 대기
                            try:
                                wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "img.n3VNCb").get_attribute('src'))
                            except:
                                time.sleep(0.1)
                            
                            # 큰 이미지 찾기
                            big_img = find_big_image(driver, wait, current_image_index)
                            if big_img:
                                # 이미지 URL 처리
                                이미지_url = process_image_url(big_img, current_image_index, collected_site_urls, driver)
                                if 이미지_url:
                                    # 즉시 다운로드 작업 제출
                                    future = executor.submit(download_image, (current_image_index, 이미지_url, save_location))
                                    futures.append(future)
                            
                            # 최소 대기 시간
                            time.sleep(0.1)
                            
                        except Exception as e:
                            logging.error(f"{current_image_index}번째 이미지 처리 중 오류 발생: {str(e)}")
                            continue
                    
                    # 모든 다운로드 작업 완료 대기
                    for future in as_completed(futures):
                        if button_frame and button_frame.is_cancelled:
                            break
                        try:
                            success = future.result()
                            if success:
                                continue # logging.info("이미지 다운로드 완료")
                        except Exception as e:
                            logging.error(f"이미지 다운로드 실패: {str(e)}")
                
            else:
                logging.error("이미지 컨테이너를 찾을 수 없습니다.")
                
        except Exception as e:
            logging.error(f"이미지 찾기 중 오류 발생: {str(e)}")
            
    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")
        
    finally:
        # 브라우저 종료
        driver.quit()
        logging.info("브라우저 종료")
        
        # 수집된 사이트 URL 리스트 출력
        if not (button_frame and button_frame.is_cancelled):
            logging.info("\n=== 수집된 사이트 URL 목록 ===")
            for index, url in sorted(collected_site_urls):
                logging.info(f"{index}번째 사이트: {url}")
            logging.info("===========================\n")
            logging.info("종료!\n")
