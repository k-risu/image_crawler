import torch
import clip
from PIL import Image
import numpy as np
import os

def generate_prompt(image_path):
    """
    이미지의 프롬프트를 생성하는 함수
    Args:
        image_path: 이미지 파일 경로
    Returns:
        str: 생성된 프롬프트
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    # 이미지 전처리
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

    # 기본 프롬프트 템플릿
    prompt_templates = [
        "a photo of {}",
        "a photograph of {}",
        "a picture of {}",
        "a high quality photo of {}",
        "a detailed photo of {}"
    ]

    # 이미지 특성 설명 텍스트
    text_descriptions = [
        # 성별 관련
        "a man", "a woman", "a male", "a female",
        # 헤어스타일 관련
        "short hair", "long hair", "curly hair", "straight hair", "wavy hair",
        "black hair", "brown hair", "blonde hair", "red hair",
        "bob haircut", "pixie cut", "undercut", "mohawk",
        # 워터마크 관련 (더 구체적인 설명 추가)
        "with visible watermark", "without any watermark", "with text watermark",
        "with logo watermark", "with signature watermark", "with copyright watermark",
        "with transparent watermark", "with semi-transparent watermark",
        "with clear watermark", "with faint watermark",
        "with no watermark", "with no text overlay", "with no logo",
        "with no signature", "with no copyright mark"
    ]

    # 모든 가능한 프롬프트 조합 생성
    all_prompts = []
    for template in prompt_templates:
        for desc in text_descriptions:
            all_prompts.append(template.format(desc))

    # 텍스트 토큰화
    text = clip.tokenize(all_prompts).to(device)

    with torch.no_grad():
        # 이미지와 텍스트 특징 추출
        image_features = model.encode_image(image)
        text_features = model.encode_text(text)
        
        # 유사도 계산
        similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
        values, indices = similarity[0].topk(10)  # 상위 10개 프롬프트 선택

    # 상위 프롬프트와 점수 조합
    top_prompts = []
    for value, idx in zip(values, indices):
        prompt = all_prompts[idx]
        score = value.item() * 100  # 백분율로 변환
        top_prompts.append(f"{prompt} ({score:.1f}%)")
    
    return "\n".join(top_prompts)

def test(log_frame):
    """
    테스트 함수
    Args:
        log_frame: 로그를 표시할 프레임
    """
    try:
        image_path = "test.jpg"  # 테스트 이미지 경로
        print(f"이미지 파일 존재 여부: {os.path.exists(image_path)}")
        print("CLIP 모델 로딩 시작...")
        prompt = generate_prompt(image_path)
        print("프롬프트 생성 완료")
        log_frame.add_log(f"생성된 프롬프트: {prompt}")
    except Exception as e:
        print(f"상세 오류: {str(e)}")
        import traceback
        print(f"오류 추적: {traceback.format_exc()}")
        log_frame.add_log(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    try:
        image_path = "test.jpg"
        print(f"이미지 파일 존재 여부: {os.path.exists(image_path)}")
        print("CLIP 모델 로딩 시작...")
        prompt = generate_prompt(image_path)
        print("\n생성된 프롬프트 (신뢰도 포함):")
        print(prompt)
        
        # 워터마크 관련 결과만 필터링하여 표시
        print("\n워터마크 관련 분석:")
        watermark_results = [line for line in prompt.split('\n') if 'watermark' in line.lower()]
        for result in watermark_results:
            print(result)
    except Exception as e:
        print(f"상세 오류: {str(e)}")
        import traceback
        print(f"오류 추적: {traceback.format_exc()}")
