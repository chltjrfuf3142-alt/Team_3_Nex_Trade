import json
from openai import OpenAI
import os
from dotenv import load_dotenv

# .env 경로 설정 (상위 폴더 탐색)
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

class PurchasingAgent:
    """
    구매/소싱 전용 AI 에이전트
    역할: 사용자 자연어 -> 관세청 검색용 표준 키워드 변환
    """
    def __init__(self):
        # ★★★ [수정] 여러 변수명 시도 + 디버깅 출력 ★★★
        api_key = (
            os.getenv("OPENAI_API_KEY") or
            os.getenv("OPEN_AI_API_KEY") or
            os.getenv("OPEN_AI_API")
        )
        
        # 디버깅: API 키 존재 여부 확인
        if not api_key:
            print("=" * 60)
            print("🚨 OpenAI API 키를 찾을 수 없습니다!")
            print(f"📁 .env 파일 위치: {env_path}")
            print(f"✓ 파일 존재 여부: {os.path.exists(env_path)}")
            print("\n현재 환경변수 값:")
            print(f"  - OPENAI_API_KEY: {bool(os.getenv('OPENAI_API_KEY'))}")
            print(f"  - OPEN_AI_API_KEY: {bool(os.getenv('OPEN_AI_API_KEY'))}")
            print(f"  - OPEN_AI_API: {bool(os.getenv('OPEN_AI_API'))}")
            print("=" * 60)
        else:
            # 성공 시 키의 앞 10자만 출력 (보안)
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