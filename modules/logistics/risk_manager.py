# modules/logistics/risk_manager.py (AI 버전)

import os
from openai import OpenAI

class StrategicGoodsAnalyzer:
    """AI 기반 전략물자 자동 판별 시스템"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    def check_strategic_goods(self, product_name):
        """
        AI를 활용한 전략물자 판별
        
        Returns:
            dict: {
                'is_strategic': bool,
                'risk_level': str (LOW/MEDIUM/HIGH/CRITICAL),
                'category': str,
                'reason': str,
                'regulations': list
            }
        """
        
        # API 키 없으면 폴백 (기존 키워드 방식)
        if not self.client:
            return self._fallback_check(product_name)
        
        try:
            # AI 프롬프트
            prompt = f"""
당신은 국제 무역 및 전략물자 전문가입니다. 아래 제품이 전략물자에 해당하는지 분석해주세요.

**제품명**: {product_name}

다음 기준으로 판단하세요:
1. 무기/군수물자 (총기, 미사일, 폭발물 등)
2. 이중용도품목 (민간/군사 겸용 - 반도체, 드론, 암호장비 등)
3. 핵/화생방 관련 물질
4. 첨단 기술 (AI, 양자컴퓨팅, 초정밀 가공기술 등)
5. 국제 제재 대상 품목

**반드시 아래 JSON 형식으로만 답변하세요:**

{{
  "is_strategic": true/false,
  "risk_level": "CRITICAL/HIGH/MEDIUM/LOW",
  "category": "무기류/이중용도/핵물질/첨단기술/일반품목",
  "reason": "판단 근거를 1-2문장으로",
  "regulations": ["적용 가능한 규제 목록"],
  "requires_license": true/false,
  "authority": "담당 기관명 (한국의 경우)"
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 빠르고 저렴한 모델
                messages=[
                    {"role": "system", "content": "You are an expert in international trade compliance and strategic goods control. Always respond in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # 일관성 중시
                max_tokens=500
            )
            
            # JSON 파싱
            import json
            result_text = response.choices[0].message.content.strip()
            
            # JSON 블록 추출 (```json ... ``` 제거)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            return result
            
        except Exception as e:
            print(f"AI 분석 오류: {e}")
            # 오류 시 폴백
            return self._fallback_check(product_name)
    
    def _fallback_check(self, product_name):
        """AI 실패 시 폴백 - 기존 키워드 방식"""
        keywords = [
            "gun", "rifle", "weapon", "총", "무기",
            "missile", "미사일", "drone", "드론",
            "nuclear", "핵", "uranium", "우라늄",
            "semiconductor", "반도체", "chip"
        ]
        
        is_strategic = any(kw.lower() in product_name.lower() for kw in keywords)
        
        return {
            'is_strategic': is_strategic,
            'risk_level': 'HIGH' if is_strategic else 'LOW',
            'category': '의심 품목' if is_strategic else '일반품목',
            'reason': '키워드 매칭 (AI 분석 실패)',
            'regulations': ['수출허가 필요 가능성 있음'] if is_strategic else [],
            'requires_license': is_strategic,
            'authority': '산업통상자원부' if is_strategic else None
        }


def analyze_cargo_context(product_name):
    """AI 기반 화물 특성 분석"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback_cargo_analysis(product_name)
    
    try:
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
물류 전문가로서 아래 제품의 운송 시 특수 요구사항을 분석해주세요.

**제품명**: {product_name}

다음 항목을 체크하세요:
1. 온도 관리 (냉동/냉장)
2. 위험물 (DG Cargo - IMDG/ADR 코드)
3. 검역 대상 (식품/의약품)
4. 고가품/귀중품
5. 중량물/과적

**JSON 형식으로만 답변:**
{{
  "special_requirements": [
    {{
      "type": "카테고리명",
      "severity": "HIGH/MEDIUM/LOW",
      "description": "구체적 설명",
      "cost_impact": "비용 영향도 (%)",
      "lead_time_impact": "리드타임 영향 (일)"
    }}
  ]
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a logistics expert. Respond only in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=600
        )
        
        import json
        result_text = response.choices[0].message.content.strip()
        
        # JSON 추출
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        data = json.loads(result_text)
        
        # Streamlit 형식으로 변환
        risks = []
        color_map = {
            'HIGH': '#f44336',
            'MEDIUM': '#ff9800', 
            'LOW': '#2196f3'
        }
        
        for req in data.get('special_requirements', []):
            severity = req.get('severity', 'MEDIUM')
            risks.append({
                "type": req.get('type', 'Unknown'),
                "msg": f"{req.get('description', 'N/A')}<br>💰 비용영향: +{req.get('cost_impact', '0')} | ⏱️ 시간: +{req.get('lead_time_impact', '0')}일",
                "color": color_map.get(severity, '#2196f3')
            })
        
        return risks
        
    except Exception as e:
        print(f"AI 화물분석 오류: {e}")
        return _fallback_cargo_analysis(product_name)


def _fallback_cargo_analysis(product_name):
    """폴백 - 기존 키워드 방식"""
    p_name = product_name.lower()
    risks = []
    
    if any(x in p_name for x in ['frozen', 'ice', '냉동', '냉장']):
        risks.append({
            "type": "Cold Chain",
            "msg": "❄️ 냉동/냉장 컨테이너 필요<br>💰 비용영향: +30% | ⏱️ 시간: +0일",
            "color": "#2196f3"
        })
    
    if any(x in p_name for x in ['battery', 'lithium', '배터리']):
        risks.append({
            "type": "Dangerous Goods",
            "msg": "🔥 위험물 승인(MSDS) 필수<br>💰 비용영향: +20% | ⏱️ 시간: +2일",
            "color": "#f44336"
        })
    
    if any(x in p_name for x in ['food', 'medicine', '식품', '약']):
        risks.append({
            "type": "Quarantine",
            "msg": "🛡️ 검역 대상<br>💰 비용영향: +10% | ⏱️ 시간: +3일",
            "color": "#ff9800"
        })
    
    return risks


# ========================================
# 기존 호환성 유지용 래퍼 함수
# ========================================
_analyzer = None

def check_strategic_goods(product_name):
    """전역 함수 - 기존 코드와 호환성 유지"""
    global _analyzer
    if _analyzer is None:
        _analyzer = StrategicGoodsAnalyzer()
    
    result = _analyzer.check_strategic_goods(product_name)
    return result['is_strategic']


def get_strategic_goods_details(product_name):
    """상세 정보 반환"""
    global _analyzer
    if _analyzer is None:
        _analyzer = StrategicGoodsAnalyzer()
    
    return _analyzer.check_strategic_goods(product_name)