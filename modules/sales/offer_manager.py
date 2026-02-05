"""
오퍼시트 관리 모듈
- 오퍼시트 폼 초기화
- 총액 계산
- 발송 내역 관리
"""

import streamlit as st
import pandas as pd


def initialize_offer_form(buyer_info: dict = None):
    """오퍼시트 폼 초기화 (prefill 처리)"""
    form = {
        "seller_name": "JJimDak.CO.",
        "seller_email": "sales@jjimdak.co.kr",
        "buyer_company": "",
        "buyer_email": "",
        "address_attn": "",
        "offer_no": "JDK2025-001",
        "date": str(pd.Timestamp.now().date()),
        "origin": "South Korea",
        "shipment": "Within 30 days after receiving L/C",
        "loading_port": "Busan, South Korea",
        "destination": "",
        "payment": "Irrevocable L/C at sight",
        "packing": "Export standard packing",
        "insurance": "To be covered by the buyer",
        "inspection": "SGS or equivalent",
        "validity": "Valid for 15 days from the date hereof",
        "claim": "Claims must be lodged within 15 days after arrival of the goods.",
        "force_majeure": "The seller shall not be liable for delays due to force majeure.",
        "arbitration": "Any disputes shall be settled by arbitration in Seoul, Korea.",
        "governing_law": "This offer shall be governed by the laws of the Republic of Korea.",
        "total_amount": "USD 0.00",
    }

    # 바이어 정보로 prefill
    if buyer_info:
        form["buyer_company"] = buyer_info.get("Name", "")
        form["buyer_email"] = buyer_info.get("Email", "")
        form["destination"] = buyer_info.get("Country", "")

    return form


def calculate_totals(items: list, margin_rate: float):
    """총 원가/판매가/이익 계산"""
    total_cost = 0.0
    total_revenue = 0.0

    for item in items:
        try:
            cost = float(item.get("cost", 0))
            quantity = float(item.get("quantity", 0))
            price = float(item.get("price", 0))

            total_cost += cost * quantity
            total_revenue += price * quantity
        except:
            pass

    total_profit = total_revenue - total_cost
    profit_rate = (total_profit / total_cost * 100) if total_cost > 0 else 0

    return {
        "total_cost": total_cost,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "profit_rate": profit_rate
    }


def save_offer_draft(offer_data: dict):
    """작성 중인 오퍼시트 세션에 저장"""
    st.session_state.offer_draft = offer_data


def get_offer_history():
    """발송 내역 조회 (session_state 기반)"""
    if 'sent_offers' not in st.session_state:
        st.session_state.sent_offers = []

    return st.session_state.sent_offers


def add_sent_offer(offer_record: dict):
    """발송 완료 오퍼 내역 추가"""
    if 'sent_offers' not in st.session_state:
        st.session_state.sent_offers = []

    st.session_state.sent_offers.append(offer_record)
