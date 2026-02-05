import os
from openai import OpenAI
from deep_translator import GoogleTranslator

# Claude(Anthropic) 라이브러리 체크
try:
    import anthropic
    HAS_CLAUDE = True
except ImportError:
    HAS_CLAUDE = False

class AIOfferWriter:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    def generate_email(self, model_choice, product, price, terms):
        """OpenAI 또는 Claude를 사용하여 오퍼 메일 작성"""
        prompt = f"""
        당신은 글로벌 무역 영업 전문가입니다.
        아래 정보를 바탕으로 바이어에게 보낼 매력적인 제안서(Offer Email)를 작성해주세요.
        
        - 품목: {product}
        - 제안가: USD {price:,.2f}
        - 조건: {terms}
        - 톤앤매너: 정중하고, 비즈니스 격식을 갖추되, 설득력 있게.
        - 언어: 한국어 (추후 번역할 예정임)
        """

        try:
            if model_choice == "Claude 3" and HAS_CLAUDE and self.anthropic_key:
                client = anthropic.Anthropic(api_key=self.anthropic_key)
                msg = client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return msg.content[0].text
            
            else: # 기본값 OpenAI
                if not self.openai_key: return "API Key가 없습니다."
                client = OpenAI(api_key=self.openai_key)
                resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                return resp.choices[0].message.content
        except Exception as e:
            return f"AI 생성 오류: {str(e)}"

    def translate(self, text, target_lang):
        """Deep Translator를 이용한 다국어 번역"""
        try:
            lang_map = {"영어 (English)": "en", "중국어 (Chinese)": "zh-CN", "일본어 (Japanese)": "ja"}
            code = lang_map.get(target_lang, "en")
            return GoogleTranslator(source='auto', target=code).translate(text)
        except Exception as e:
            return f"번역 오류: {str(e)}"