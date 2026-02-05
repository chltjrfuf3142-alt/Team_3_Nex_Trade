import streamlit as st
import os
import sys
import time
from dotenv import load_dotenv
from modules.ui import setup_app_style, render_sidebar, render_top_navbar

setup_app_style()
render_top_navbar()  # ← 파라미터 없이 그냥 호출!
# ... 나머지 코드 ...

# 0. 환경변수 로드
load_dotenv()

# 1. 모듈 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 2. 페이지 기본 설정 (반드시 맨 처음에!)
st.set_page_config(
    page_title="TradeNex System",
    page_icon="🌏",
    layout="wide"
)

# 3. UI 모듈 불러오기
try:
    from modules.ui import setup_app_style, render_sidebar, render_top_navbar, render_gradient_header
except ImportError:
    st.error("modules/ui.py 파일을 찾을 수 없습니다.")
    st.stop()

# 4. 스타일 적용
setup_app_style()

# ==============================================================================
# [함수 1] 로그인 화면
# ==============================================================================
def show_login_page():
    """로그인 전: 메인 화면에 로그인 창만 표시"""

    # 배경색 흰색 + 사이드바/네비바 숨김
    st.markdown("""
    <style>
    /* 로그인 페이지 배경색 */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    /* 로그인 화면에서는 사이드바 완전히 숨김 */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* 로그인 화면에서는 네비바 숨김 */
    .fixed-navbar {
        display: none !important;
    }
    
    /* 로그인 화면에서는 상단 여백 제거 */
    .main .block-container {
        padding-top: 0 !important;
    }
    
    /* 로고 글자 스타일 - 여기가 추가된 부분! */
    .login-logo-text {
        color: #FFFFFF !important;
        font-size: 7rem !important;
        font-weight: 900 !important;
        margin: 0 !important;
        font-style: italic !important;
        font-family: 'Arial Black', Arial, sans-serif !important;
        letter-spacing: -2px !important;
        line-height: 1 !important;
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input {
        background-color: #F8F9FA;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 14px;
        font-size: 0.95rem;
        color: #333;
    }

    .stTextInput > div > div > input:focus {
        border-color: #5B9BD5;
        box-shadow: 0 0 0 2px rgba(91, 155, 213, 0.1);
    }

    /* 버튼 스타일 */
    .stButton > button {
        background-color: #5B9BD5 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 14px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s !important;
    }

    .stButton > button:hover {
        background-color: #4A8FD8 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(91, 155, 213, 0.3) !important;
    }

    /* 체크박스 스타일 */
    .stCheckbox {
        margin-top: 10px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 상단 여백
    st.markdown("<br><br><br>", unsafe_allow_html=True)

    # 중앙 정렬
    # 중앙 정렬 (가운데 컬럼을 훨씬 넓게)
    col1, col2, col3 = st.columns([0.3, 2.4, 0.3])

    with col2:
        # 로고 (독립된 박스) - 여기가 수정된 부분!
        st.markdown("""
            <div style="background: linear-gradient(135deg, #5B9BD5 0%, #4A8FD8 100%); 
                        padding: 60px 40px; 
                        border-radius: 12px;
                        box-shadow: 0 6px 20px rgba(91, 155, 213, 0.25);
                        text-align: center;
                        margin-bottom: 30px;">
                <div class="login-logo-text">NexTrade</div>
            </div>
        """, unsafe_allow_html=True)

        # 아이디 입력
        user_id = st.text_input(
            "아이디",
            placeholder="아이디",
            label_visibility="collapsed",
            key="login_id"
        )

        # 비밀번호 입력
        user_pw = st.text_input(
            "비밀번호",
            type="password",
            placeholder="비밀번호",
            label_visibility="collapsed",
            key="login_pw"
        )

        # 로그인 상태 유지
        remember = st.checkbox("로그인 상태 유지")

        # 로그인 버튼
        if st.button("로그인", type="primary", use_container_width=True):
            if user_id == "박도영" and user_pw == "1234":
                st.success(f"✓ 접속 승인! 환영합니다, {user_id}님.")
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = user_id
                time.sleep(1)
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 틀렸습니다.")

        # 하단 링크
        st.markdown("""
            <div style="text-align: center; margin-top: 20px;">
                <span style="color: #9CA3AF; font-size: 0.9rem; cursor: pointer;">아이디 찾기</span>
                <span style="color: #D1D5DB; margin: 0 8px;">|</span>
                <span style="color: #9CA3AF; font-size: 0.9rem; cursor: pointer;">비밀번호 재설정</span>
            </div>
        """, unsafe_allow_html=True)
# ==============================================================================
# [함수 2] 메인 대시보드 (파란색 통일 버전)
# ==============================================================================
def show_main_dashboard():
    """로그인 후: 파란색으로 통일된 카드형 워크플로우 화면"""

    # 배경색 흰색으로 변경 + 사이드바 표시
    st.markdown("""
    <style>
    .stApp {
        background-color: white !important;
    }
    
    /* 로그인 후에는 사이드바 표시 */
    [data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ------------------- [상단 네비게이션 바] -------------------
    render_top_navbar(current_page="home")

    # ------------------- [그라데이션 헤더] -------------------
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, #5B9BD5 0%, #4A8BC2 50%, #F8F9FA 100%);
        height: 160px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(91, 155, 213, 0.2);
        display: flex;
        align-items: center;
        padding-left: 50px;
    ">
        <span style='
            font-size: 6rem; 
            font-weight: 1500; 
            color: white; 
            letter-spacing: 8px; 
            text-shadow: 
                3px 3px 0px rgba(0,0,0,0.1),
                5px 5px 10px rgba(0,0,0,0.2),
                0 0 20px rgba(255,255,255,0.3);
            font-family: "Arial Black", Arial, sans-serif;
            font-style: italic;
        '>
            NexTrade ERP
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ------------------- [1. 사용자 정보 & 시간] -------------------
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"**AX Master** |  **{st.session_state['user_id']}**")
    with col_h2:
        st.markdown(f"""
        <div style='text-align:right; font-size:1.0rem; font-weight:600; color:#475569;'>
            {time.strftime('%Y-%m-%d')}<br>
            <span style="color:#3B82F6;">{time.strftime('%H:%M')} KST</span>
        </div>
        """, unsafe_allow_html=True)
    # ------------------- [2. 환영 메시지] -------------------
    st.markdown(f"### 안녕하세요, {st.session_state['user_id']}님")
    st.markdown("NexTrade 통합 ERP 시스템에 오신걸 환영합니다.")
    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------- [3. 파란색 통일 카드 디자인] -------------------
    
    # ★★★ CSS 스타일 주입 (모든 카드를 파란색 계열로 통일) ★★★
    st.markdown("""
    <style>
    .fingle-card {
        padding: 25px;
        border-radius: 20px;
        color: white;
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 10px 20px rgba(91, 155, 213, 0.2);
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }
    .fingle-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(91, 155, 213, 0.35);
    }
    .card-step { 
        font-size: 0.9rem; 
        font-weight: 600; 
        opacity: 0.9; 
        margin-bottom: 5px; 
    }
    .card-title { 
        font-size: 1.6rem; 
        font-weight: 800; 
        margin-bottom: 10px; 
        line-height: 1.2; 
    }
    .card-desc { 
        font-size: 0.95rem; 
        opacity: 0.95; 
        line-height: 1.5; 
    }
    
    /* ★★★ 모든 카드를 로그인 화면 파란색 계열로 통일 ★★★ */
    
    /* 1. 구매팀 - 메인 파란색 */
    .bg-blue-1 { 
        background: linear-gradient(135deg, #5B9BD5 0%, #4A8FD8 100%); 
    }
    
    /* 2. 물류팀 - 약간 진한 파란색 */
    .bg-blue-2 { 
        background: linear-gradient(135deg, #4A8FD8 0%, #3B7DC2 100%); 
    }
    
    /* 3. 영업팀 - 하늘색 계열 */
    .bg-blue-3 { 
        background: linear-gradient(135deg, #6AAFE6 0%, #5B9BD5 100%); 
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # ★★★ [CARD 1] 구매 관리 (파란색 버전 1) ★★★
    with col1:
        st.markdown("""
        <div class="fingle-card bg-blue-1">
            <div>
                <div class="card-step">STEP 01</div>
                <div class="card-title">Purchasing<br>Management</div>
                <div class="card-desc">
                    <b>"무엇을 팔 것인가?"</b><br>
                    AI 소싱 및 공급사 리스크 진단
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # 버튼을 카드 바로 밑에 배치
        if st.button("구매 업무 시작", use_container_width=True, key="btn_step1"):
            st.switch_page("pages/purchasing_1.py")

    # ★★★ [CARD 2] 물류 관리 (파란색 버전 2) ★★★
    with col2:
        st.markdown("""
        <div class="fingle-card bg-blue-2">
            <div>
                <div class="card-step">STEP 02</div>
                <div class="card-title">Logistics<br>Optimization</div>
                <div class="card-desc">
                    <b>"어떻게 가져올 것인가?"</b><br>
                    운송 루트 설계 및 비용 산출
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("물류 업무 시작", use_container_width=True, key="btn_step2"):
            st.switch_page("pages/logistics_1.py")

    # ★★★ [CARD 3] 영업 관리 (파란색 버전 3) ★★★
    with col3:
        st.markdown("""
        <div class="fingle-card bg-blue-3">
            <div>
                <div class="card-step">STEP 03</div>
                <div class="card-title">Sales &<br>Offer Sheet</div>
                <div class="card-desc">
                    <b>"얼마에 팔 것인가?"</b><br>
                    마진 시뮬레이션 및 오퍼 발행
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("영업 업무 시작", use_container_width=True, key="btn_step3"):
            st.switch_page("pages/sale_1.py")

    # ------------------- [4. 하단 버전 정보] -------------------
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; color:#CBD5E1; font-size:0.8rem;'>
        TradeNex Integrated System v1.0 | Powered by OpenAI & Tavily
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# [메인 실행 로직]
# ==============================================================================
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        show_login_page()
    else:
        render_sidebar()
        show_main_dashboard()

if __name__ == "__main__":
    main()