import os   

from image_download import image_download


if __name__ == "__main__":
    # 사용 예시
    url = "https://www.google.com/search?q=헤어모델&tbm=isch&tbs=isz:l"  # 구글 이미지 검색 URL (큰 이미지만)
    class_names = "YQ4gaf"  # 찾고자 하는 이미지의 클래스 이름
    
    image_download(url, class_names, 5)  # 5장의 이미지 다운로드 