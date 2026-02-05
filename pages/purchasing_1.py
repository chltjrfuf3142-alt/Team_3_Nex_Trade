import streamlit as st
import sys
import os
from modules.ui import setup_app_style, render_sidebar, render_top_navbar

setup_app_style()
render_top_navbar()  # ← 파라미터 없이 그냥 호출!
# ... 나머지 코드 ...

# [중요] set_page_config는 home.py에서 이미 설정됨
# Streamlit pages 시스템에서는 메인 파일에서만 설정 가능하므로 주석 처리
# st.set_page_config(page_title="TradeNex Purchasing", page_icon="🛒", layout="wide")

# -------------------------------------------------------------------------
# [Setup] UI 및 경로 설정
# -------------------------------------------------------------------------
try:
    from modules.ui import setup_app_style, display_header, render_sidebar, render_top_navbar
    setup_app_style()
    render_top_navbar(current_page="purchasing")  # 상단 네비게이션 바
    render_sidebar()  # 사이드바

    # 뒤로가기 버튼
    if st.button("← 뒤로가기", key="back_to_home"):
        st.switch_page("home.py")

    display_header("글로벌 소싱 & 구매", "상품 발굴부터 견적 의뢰까지")
except ImportError:
    pass # UI 모듈 없으면 패스

# 모듈 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

# -------------------------------------------------------------------------
# [Import] 모듈 불러오기 (여기에 Inquiry 추가됨!)
# -------------------------------------------------------------------------
try:
    # 각 파일 안에 해당 함수 이름(def run_...)이 정확히 있어야 합니다.
    from modules.purchasing.item_searcher import run_item_searcher
    from modules.purchasing.risk_screening import run_risk_screening
    from modules.purchasing.inquiry_maker import run_inquiry_maker # <--- [추가]
except ImportError as e:
    st.error(f"모듈을 불러올 수 없습니다. 폴더 구조를 확인해주세요. ({e})")

# -------------------------------------------------------------------------
# [View] 탭 구성 및 실행
# -------------------------------------------------------------------------
st.title("글로벌 소싱 & 구매")

# 탭 구성
tab1, tab2, tab3 = st.tabs([
    "상품 발굴",
    "리스크 평가",
    "견적서 작성"
])

with tab1:
    if 'run_item_searcher' in globals():
        run_item_searcher()

with tab2:
    if 'run_risk_screening' in globals():
        run_risk_screening()

with tab3: # <--- [추가]
    if 'run_inquiry_maker' in globals():
        run_inquiry_maker()

# 마지막 탭 맨 아래
    st.markdown("---")
    
    col_left, col_center, col_right = st.columns([1, 1, 1])
    with col_center:
        st.markdown("### 다음 단계")
        if st.button("🚚 물류팀 페이지로 이동", type="primary", use_container_width=True):
            st.switch_page("pages/logistics_1.py")