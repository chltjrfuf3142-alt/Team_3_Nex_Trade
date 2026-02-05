"""
═══════════════════════════════════════════════════════════════════
  NexTrade Sales - 탭 기반 구조 (수정 버전)
═══════════════════════════════════════════════════════════════════
  Tab 1: 시장조사 & 바이어 발굴
  Tab 2: 오퍼시트 생성 (자동 송부 기능 포함)
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import streamlit as st
import pandas as pd
from modules.ui import setup_app_style, render_sidebar, render_top_navbar

setup_app_style()
render_top_navbar()  # ← 파라미터 없이 그냥 호출!
# ... 나머지 코드 ...

# ═══════════════════════════════════════════════════════════════
#  경로 설정
# ═══════════════════════════════════════════════════════════════

current_dir = os.path.dirname(os.path.abspath(__file__))  # pages/ 폴더
parent_dir = os.path.dirname(current_dir)                  # Nex_Trade/ 루트
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(parent_dir, '.env'))

# ═══════════════════════════════════════════════════════════════
#  UI 모듈 import
# ═══════════════════════════════════════════════════════════════

try:
    from modules.ui import setup_app_style, display_header, render_sidebar, render_top_navbar
except ImportError:
    pass  # UI 모듈이 없으면 패스

# ═══════════════════════════════════════════════════════════════
#  데이터 파일 초기화
# ═══════════════════════════════════════════════════════════════

def ensure_data_files():
    """필수 CSV 파일들을 생성합니다."""

    # 데이터 폴더 경로 설정
    data_sales_dir = os.path.join(parent_dir, "data", "sales")
    os.makedirs(data_sales_dir, exist_ok=True)

    margin_file = os.path.join(data_sales_dir, "margin.csv")
    buyers_file = os.path.join(data_sales_dir, "global_buyers.csv")

    # 마진율 로직 파일
    if not os.path.exists(margin_file):
        df_margin = pd.DataFrame({
            "Category_Code": ["GEN", "FUN", "PRE"],
            "Category_Name": ["General (일반/음료)", "Functional (기능성)", "Premium (프리미엄)"],
            "Target_Product": [
                "비타민 음료, 이온음료",
                "건강기능식품(비타민, 유산균)",
                "고가 홍삼, 녹용, 선물세트"
            ],
            "Benchmark_Company": ["동아오츠카 (일반 유통)", "종근당 (헬스케어)", "정관장 (브랜드 명품)"],
            "Margin_Rate": [0.28, 0.45, 0.96],
            "Logic_Summary": [
                "박리다매형 시장. 동아오츠카 상품매출이익률(28%) 적용하여 가격 경쟁력 확보",
                "★주력 모델. 효능 입증 제품. 종근당 상품이익률(45%) 적용하여 수익성 확보",
                "고소득층 타겟. 정관장 원가율 역산(96%) 적용하여 프리미엄 이미지 구축"
            ]
        })
        df_margin.to_csv(margin_file, index=False, encoding='utf-8-sig')

    # 글로벌 바이어 데이터 (몽골 전용)
    if not os.path.exists(buyers_file):
        data = [
            [1,"몽골","Monos Group (모노스 그룹)","Healthcare & Pharma",1990,"80M USD","몽골 최대 제약 그룹으로 자체 약국 체인을 통한 고기능성 영양제 공략에 최적.","info@monos.mn"],
            [2,"몽골","Nomin United (노민 유나이티드)","Retail & Distribution",1992,"100M USD","백화점 및 대형마트 운영사로 대중적인 비타민 및 홍삼 입점에 유리.","nomin@nomin.net"],
            [3,"몽골","Tavan Bogd (타반 보그드)","Conglomerate",1995,"120M USD","글로벌 브랜드 파트너십에 강점이 있어 인지도 높은 한국 제품 선호.","info@tavanbogd.com"],
            [4,"몽골","CU Mongolia (센트럴 익스프레스)","Convenience Store",2018,"30M USD","젊은 층 타겟의 다이어트 젤리 및 소포장 건기식 공략에 최적화.","info@cumongol.mn"],
            [5,"몽골","Emart Mongolia (이마트 몽골)","Hypermarket",2016,"45M USD","한국 이마트 파트너사 운영으로 한국 제품에 대한 이해도가 매우 높음.","online@e-mart.mn"],
            [6,"몽골","EuroPharma (유로 파마)","Pharmacy Chain",2005,"15M USD","현대식 전문 약국 체인으로 한국산 어린이 영양제 수요가 집중되는 곳.","info@europharma.com.mt"],
            [7,"몽골","Asia Pharma (아시아 파마)","Medical Import",2002,"20M USD","병원 및 약국 전문 공급사로 식약처 인증 기능성 제품 제안 시 효과적.","marketing@asiapharma.mn"],
            [8,"몽골","Monos Pharos (모노스 파로스)","Brand Distributor",2010,"10M USD","모노스 그룹 내 수입 전담팀으로 독점 계약 및 브랜드 총판 논의 시 필수.","trade.assistant@monospharmatrade.mn"],
            [9,"몽골","BOSA Holding (보사 홀딩스)","Food Distributor",1998,"25M USD","한국 식품 수입 경험이 풍부하며 건강 음료 및 홍삼 라인업 확장에 열성적.","info@bosa.mn"],
            [10,"몽골","Everyday Farm (에브리데이 팜)","Premium Market",2008,"10M USD","고소득층 타겟 유기농 및 친환경 보조식품 제안 시 승산이 높음.","info@everyday.mn"]
        ]
        df = pd.DataFrame(data, columns=["id","Country","Name","Business","Founded","Capital","Description","Email"])
        df.to_csv(buyers_file, index=False, encoding='utf-8-sig')

ensure_data_files()

# ═══════════════════════════════════════════════════════════════
#  Session State 초기화
# ═══════════════════════════════════════════════════════════════

def initialize_session_state():
    """세션 초기화 (앱 시작 시 1회 호출)"""
    defaults = {
        # Tab 1: 시장조사 & 바이어
        'target_product': '',
        'target_country': '',
        'buyer_list': [],
        'selected_buyer_ids': [],
        'selected_buyers_full': [],

        # Tab 2: 오퍼시트
        'num_items': 3,
        'offer_draft': {},
        'generated_offers': [],

        # 공통
        'is_logged_in': False,
        'user_id': 'Guest',
        'messages': [{"role": "assistant", "content": "시스템: 무엇을 도와드릴까요?"}]
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ═══════════════════════════════════════════════════════════════
#  메인 앱
# ═══════════════════════════════════════════════════════════════

def main():
    # UI 설정
    try:
        setup_app_style()
        render_top_navbar(current_page="sales")
        render_sidebar()
    except:
        pass  # UI 모듈이 없으면 패스

    # 뒤로가기 버튼
    if st.button("← 뒤로가기", key="back_to_home_sales"):
        st.switch_page("home.py")

    # 헤더
    try:
        display_header("영업 관리 시스템", "바이어 발굴부터 오퍼시트 생성까지")
    except:
        st.markdown("""<div class="main-header">
            <span class="brand-text">NexTrade</span>
            <span class="brand-sub">Sales Edition</span>
        </div>""", unsafe_allow_html=True)

    # Session State 초기화
    initialize_session_state()

    # 사이드바
    with st.sidebar:
        if st.button("홈으로 (초기화)", use_container_width=True):
            st.session_state.target_product = ''
            st.session_state.target_country = ''
            st.session_state.buyer_list = []
            st.session_state.selected_buyer_ids = []
            st.rerun()

        if not st.session_state.is_logged_in:
            st.markdown('<div class="sb-card">', unsafe_allow_html=True)
            st.markdown('<span style="font-weight:700;">임직원 로그인</span>', unsafe_allow_html=True)
            st.text_input("ID", placeholder="사번", label_visibility="collapsed", key="lid")
            st.text_input("PW", type="password", placeholder="비밀번호", label_visibility="collapsed", key="lpw")
            if st.button("로그인", type="secondary", use_container_width=True):
                st.session_state.is_logged_in = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="sb-card" style="text-align:center;">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:3rem;">🐣</div>', unsafe_allow_html=True)
            st.markdown('**박사원**<br><span style="color:#64748B;">영업 1팀 / 사원</span>', unsafe_allow_html=True)
            if st.button("로그아웃", type="secondary", use_container_width=True):
                st.session_state.is_logged_in = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # ★★★ 탭 구성 (Tab3 제거) ★★★
    tab1, tab2 = st.tabs([
        "🔍 시장조사 & 바이어",
        "📝 오퍼시트 생성"
    ])

    # Tab 핸들러 import
    try:
        from modules.sales.tab_handlers import run_market_research, run_offer_generator
    except ImportError as e:
        st.error(f"모듈을 불러올 수 없습니다: {e}")
        return

    with tab1:
        run_market_research()

    with tab2:
        run_offer_generator()

    # 푸터
    st.markdown("<div class='footer'>NexTrade 통합 시스템 v2.0 © 2026</div>",
                unsafe_allow_html=True)

if __name__ == "__main__":
    main()