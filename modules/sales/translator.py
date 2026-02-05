"""
OpenAI 번역 모듈
- Offer Sheet 데이터를 다국어로 번역
- 국가별 언어 및 플래그 정보 제공
"""

import os
import json
import streamlit as st


# 국가별 언어 정보
COUNTRIES = {
    "None (English Only)": {"language": None, "flag": "🇬🇧"},
    "Mongolia": {"language": "Mongolian", "flag": "🇲🇳"},
    "China": {"language": "Chinese", "flag": "🇨🇳"},
    "Japan": {"language": "Japanese", "flag": "🇯🇵"},
    "Korea": {"language": "Korean", "flag": "🇰🇷"},
    "Vietnam": {"language": "Vietnamese", "flag": "🇻🇳"},
    "Thailand": {"language": "Thai", "flag": "🇹🇭"},
    "Russia": {"language": "Russian", "flag": "🇷🇺"},
    "Saudi Arabia": {"language": "Arabic", "flag": "🇸🇦"},
    "Spain": {"language": "Spanish", "flag": "🇪🇸"},
    "France": {"language": "French", "flag": "🇫🇷"},
    "Germany": {"language": "German", "flag": "🇩🇪"},
    "Portugal": {"language": "Portuguese", "flag": "🇵🇹"},
    "Indonesia": {"language": "Indonesian", "flag": "🇮🇩"},
    "Malaysia": {"language": "Malay", "flag": "🇲🇾"},
    "Turkey": {"language": "Turkish", "flag": "🇹🇷"},
    "India": {"language": "Hindi", "flag": "🇮🇳"},
    "Philippines": {"language": "Filipino", "flag": "🇵🇭"},
    "Italy": {"language": "Italian", "flag": "🇮🇹"},
}


def translate_offer_data(form_data: dict, items: list, target_language: str):
    """OpenAI API를 사용하여 Offer Sheet 번역"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ OPENAI_API_KEY가 .env에 없습니다.")
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
    except ImportError:
        st.error("⚠️ openai 패키지 설치 필요: `pip install openai`")
        return None

    translate_payload = {
        "company_name": "NexTrade",
        "company_address": "GangNam-Gu 9 Gil Coex 4th floor",
        "seller_company": "JIMDAK CORP.",
        "intro_text": "We are pleased to offer you the following goods on the terms and conditions set forth below.",
        "labels": {
            "offer_sheet": "OFFER SHEET",
            "messrs": "Messrs",
            "offer_no": "Offer No.",
            "date": "Date",
            "origin": "Origin",
            "shipment": "Shipment",
            "loading_port": "Loading Port",
            "destination": "Destination",
            "payment": "Payment",
            "packing": "Packing",
            "insurance": "Insurance",
            "inspection": "Inspection",
            "validity": "Validity",
            "no": "No.",
            "description_of_goods": "Description of Goods",
            "quantity": "Quantity",
            "unit_price": "Unit Price",
            "amount": "Amount",
            "total_amount": "TOTAL AMOUNT (FOB/CIF/CFR)",
            "claim": "Claim",
            "force_majeure": "Force Majeure",
            "arbitration": "Arbitration",
            "governing_law": "Governing Law",
            "accepted_by_buyer": "ACCEPTED BY (Buyer)",
            "yours_faithfully": "Yours Faithfully",
            "authorized_signature": "Authorized Signature",
        },
        "values": {k: form_data.get(k, "") for k in [
            "messrs", "buyer_company", "address_attn", "offer_no", "date",
            "origin", "shipment", "loading_port", "destination", "payment",
            "packing", "insurance", "inspection", "validity",
            "claim", "force_majeure", "arbitration", "governing_law", "total_amount"
        ]},
        "items": [
            {"no": it["no"], "description": it["description"],
             "quantity": it["quantity"], "unit_price": it["unit_price"], "amount": it["amount"]}
            for it in items if it["description"].strip()
        ],
    }

    prompt = f"""Translate ALL text content in the following Offer Sheet data from English to {target_language}.

CRITICAL RULES:
1. Translate ALL labels, values, and text content completely to {target_language}
2. EXCEPTION: Keep the following in English:
   - Company names: NexTrade, JIMDAK CORP.
   - Currency: USD
   - Trade terms: FOB, CIF, CFR, L/C
   - Numbers and dates
3. Everything else must be translated to {target_language}
4. Return ONLY valid JSON with exact same structure
5. No extra text, no markdown, just pure JSON

Data:
{json.dumps(translate_payload, ensure_ascii=False, indent=2)}
"""

    try:
        with st.spinner(f"🌐 {target_language} 번역 중..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional translator. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000,
            )

            result_text = response.choices[0].message.content.strip()

            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            translated = json.loads(result_text)
            return translated

    except json.JSONDecodeError as e:
        st.error(f"⚠️ JSON 파싱 오류: {e}")
        return None
    except Exception as e:
        st.error(f"⚠️ OpenAI API 오류: {e}")
        return None
