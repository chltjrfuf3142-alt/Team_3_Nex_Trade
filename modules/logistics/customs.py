import os
import sys
import json
from openai import OpenAI

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from config import get_env

class CustomsBroker:
    """
    [AI Customs Broker]
    자연어 검색 -> HS Code & 관세율 동시 추론
    """
    def __init__(self):
        # 클라우드 + 로컬 환경 지원
        api_key = get_env("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    # [중요] 여기 'country' 파라미터가 있어야 에러가 안 납니다!
    def get_hs_code_and_duty(self, product_name, country="Mongolia"):
        """
        통합 함수: 제품명과 국가를 주면 {코드, 관세율} 딕셔너리를 반환
        """
        # 1. API 키 없음 -> 비상용 기본값
        if not self.client:
            return {"hs_code": "2106.90", "duty_rate": 8.0}

        # 2. AI에게 물어보기
        prompt = f"""
        Act as a Customs Broker.
        Target Product: '{product_name}'
        Target Country: {country}
        
        Task:
        1. Identify the most likely HS Code (6-digit).
        2. Estimate the import duty rate (%) for this country.
        
        Output Format: JSON ONLY.
        {{
            "hs_code": "XXXX.XX",
            "duty_rate": number
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # 혹은 gpt-3.5-turbo
                messages=[
                    {"role": "system", "content": "You are a JSON-speaking customs expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            
            content = response.choices[0].message.content.strip()
            # JSON 파싱 (마크다운 등 불순물 제거)
            if "```" in content:
                import re
                content = re.sub(r"```json|```", "", content).strip()
                
            return json.loads(content)

        except Exception as e:
            print(f"AI Error: {e}")
            # 에러 나면 안전장치 값 반환
            return {"hs_code": "0000.00", "duty_rate": 8.0}