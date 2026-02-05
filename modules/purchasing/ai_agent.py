import json
from openai import OpenAI
import os
import sys

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from config import get_env

class PurchasingAgent:
    """
    구매/소싱 전용 AI 에이전트
    역할: 사용자 자연어 -> 관세청 검색용 표준 키워드 변환
    """
    def __init__(self):
        # 클라우드 + 로컬 환경 지원
        api_key = get_env("OPENAI_API_KEY")

        if not api_key:
            print("🚨 OpenAI API 키를 찾을 수 없습니다!")
        else:
            print(f"✅ OpenAI API 키 로드 성공: {api_key[:10]}...")

        self.client = OpenAI(api_key=api_key) if api_key else None
        self.api_available = bool(api_key)
        
    def refine_search_term(self, user_query):
        """
        사용자 입력 -> 관세청 API 검색용 키워드 리스트(JSON) 변환
        
        Returns:
            list: 성공 시 키워드 리스트, 실패 시 None
        """
        # ★★★ [핵심 수정] 에러 시 None 반환 (문자열 X) ★★★
        if not self.client:
            print("⚠️ OpenAI 클라이언트가 초기화되지 않았습니다.")
            return None
            
        prompt = f"""
        [Task]
        사용자가 입력한 상품명("{user_query}")을 분석하여, 관세청 HS코드 조회 시스템에서 검색 결과가 가장 잘 나올법한 **'표준 품명'** 또는 **'HS코드(숫자)'** 3가지를 추천하라.
        
        [Condition]
        1. 은어/속어는 배제하고 공식 무역 용어로 변환할 것.
        2. 예: "마시는 수액" -> ["혼합음료", "전해질 음료", "2202"]
        3. 예: "갤탭" -> ["태블릿 PC", "847130", "무선통신기기"]
        
        [Output]
        JSON String List only. No explanation.
        Example: ["키워드1", "키워드2", "키워드3"]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            print(f"✅ AI 키워드 변환 성공: {user_query} → {result}")
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 실패: {e}")
            return None
        except Exception as e:
            print(f"❌ AI 호출 실패: {e}")
            return None