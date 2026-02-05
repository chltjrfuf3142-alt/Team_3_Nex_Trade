# modules/logistics/ai_agent.py

import os
import sys
from openai import OpenAI

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from config import get_env

class AIAgent:
    """물류 AI 컨설턴트"""

    def __init__(self, api_key=None):
        self.api_key = api_key or get_env("OPENAI_API_KEY")
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    def ask_strategy(self, country, incoterm, product):
        """
        종합 물류 전략 리포트 생성
        
        Args:
            country: 목적지 국가 (예: "Mongolia", "Kazakhstan")
            incoterm: 인코텀즈 조건 (예: "DDP", "FOB")
            product: 제품명 (예: "말보루 레드")
        
        Returns:
            str: 마크다운 형식의 전략 리포트
        """
        
        if not self.client:
            return self._fallback_response(country, incoterm, product)
        
        try:
            # ========================================
            # 원래 프롬프트 형식 복원
            # ========================================
            prompt = f"""
[Role Definition]
당신은 종합상사에서 20년 근무한 베테랑 물류/무역 컨설턴트입니다.
냉철하고 전문적인 어조로, 핵심만 요약해서 답변하십시오.

[Scenario]
- 수출 품목: {product}
- 타겟 국가: {country}
- 계약 조건: {incoterm} (Incoterms 2020)

[Request]
위 조건을 분석하여 아래 3가지 항목을 작성해 주십시오. (마크다운 포맷 사용)

1.  필수 선적 서류 (Top 3): {country} 통관 시 누락하면 안 되는 서류.
2.  물류 리스크 분석: 해당 지역/루트의 잠재적 위험 요소 (TCR 철도 등 고려).
3.  협상 전략: 수출자(Seller) 입장에서 마진을 방어하기 위한 한 줄 조언.
"""
            
            # AI 호출
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a senior trade consultant with 20+ years of experience. Be concise and professional."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            report = response.choices[0].message.content.strip()
            
            # 리포트 헤더 추가
            import time
            
            header = f"""
# TradeNex AI 전략 리포트

**생성 일시**: {time.strftime('%Y년 %m월 %d일 %H:%M:%S')}  
**제품**: {product}  
**목적지**: {country}  
**거래조건**: {incoterm}

---

"""
            
            footer = """

---

## 📞 추가 지원

본 리포트는 AI 분석을 기반으로 작성되었습니다.  
구체적인 법률 자문이나 맞춤 컨설팅이 필요하신 경우, 영업팀에 문의해주세요.

**TradeNex 고객센터**: support@tradenex.ai  
**긴급 연락처**: +82-2-1234-5678
"""
            
            final_report = header + report + footer
            
            return final_report
            
        except Exception as e:
            print(f"AI 리포트 생성 오류: {e}")
            return self._fallback_response(country, incoterm, product)
    
    def _fallback_response(self, country, incoterm, product):
        """AI 실패 시 기본 템플릿 반환"""
        import time
        
        return f"""
# 🎯 TradeNex 물류 전략 리포트

**생성 일시**: {time.strftime('%Y년 %m월 %d일 %H:%M:%S')}  
**제품**: {product}  
**목적지**: {country}  
**거래조건**: {incoterm}

---

## ⚠️ AI 분석 일시 중단

현재 AI 서비스에 일시적인 문제가 발생하여 기본 가이드를 제공합니다.

## 📄 필수 선적 서류 (Top 3)

1. **Commercial Invoice** (원본)
   - 거래 금액, 품목 상세 기재 필수
   
2. **Packing List**
   - 컨테이너별 적재 내역 상세 기술
   
3. **Certificate of Origin**
   - FTA 적용을 위한 원산지 증명서 (Form MK/RCEP)

## ⚠️ 물류 리스크 분석

### 주요 리스크:
- **국경 통과 지연**: {country} 통관 프로세스 평균 3-5일 소요
- **철도 운송 불확실성**: TCR/TMGR 노선의 계절별 지연 가능성
- **외환 변동성**: 현지 통화 환율 급등락 리스크

### 권장 조치:
- 화물 추적 시스템 활용 필수
- 보험 가입 (CIF/CIP 조건 권장)

## 💡 협상 전략

**핵심 조언**: {incoterm} 조건에서는 [운송비/보험료/관세] 부담 주체가 명확해야 합니다.  
→ **가격 산정 시 리스크 프리미엄 3-5% 반영** 권장

---

## 📞 문의하기

상세한 컨설팅이 필요하시면 석렬이한테 연락주지 마세요.

**TradeNex 고객센터**: seokryeol@tradenex.ai  
**긴급 연락처**: +82-10-1234-5678
"""