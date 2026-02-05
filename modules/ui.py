import streamlit as st
import os
import time
from openai import OpenAI

def setup_app_style():
    """
    TradeNex 통합 UI 스타일링 (Global CSS) - Design Enhanced
    """
    st.markdown("""
        <style>
        /* ═══════════════════════════════════════════════════════════════ */
        /* 1. 폰트 및 타이포그래피 통일 */
        /* ═══════════════════════════════════════════════════════════════ */
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

        html, body, [class*="css"], font, button, input, textarea {
            font-family: 'Pretendard', sans-serif !important;
        }

        /* 제목 레벨별 폰트 크기 및 굵기 통일 */
        h1 { font-size: 2.0rem !important; font-weight: 700 !important; color: #1E293B !important; }
        h2 { font-size: 1.6rem !important; font-weight: 700 !important; color: #1E293B !important; }
        h3 { font-size: 1.3rem !important; font-weight: 600 !important; color: #334155 !important; }
        h4 { font-size: 1.1rem !important; font-weight: 600 !important; color: #475569 !important; }
        h5 { font-size: 1.0rem !important; font-weight: 500 !important; color: #64748B !important; }

        /* 본문 텍스트 */
        p, div, span, label { font-size: 0.95rem !important; font-weight: 400 !important; }

        /* [핵심] 기본 사이드바 메뉴 숨기기 */
        [data-testid="stSidebarNav"] { display: none !important; }

        /* ═══════════════════════════════════════════════════════════════ */
        /* Streamlit 기본 헤더 완전히 제거 */
        /* ═══════════════════════════════════════════════════════════════ */
        [data-testid="stHeader"] {
            display: none !important;
            height: 0 !important;
            visibility: hidden !important;
        }
        
        header[data-testid="stHeader"] {
            display: none !important;
        }

        /* ═══════════════════════════════════════════════════════════════ */
        /* 2. 상단 네비게이션 바 (고정) */
        /* ═══════════════════════════════════════════════════════════════ */
        .top-navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background-color: #F8FAFC;
            border-bottom: 2px solid #E2E8F0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 30px;
            z-index: 999999 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .top-navbar-logo {
            font-size: 1.4rem;
            font-weight: 800;
            color: #1E293B;
        }

        .top-navbar-buttons {
            display: flex;
            gap: 15px;
        }

        .top-navbar-btn {
            padding: 8px 20px;
            background-color: white;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            color: #475569;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
        }

        .top-navbar-btn:hover {
            border-color: #3B82F6;
            color: #3B82F6;
            background-color: #EFF6FF;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);
        }

        .top-navbar-btn.active {
            background-color: #3B82F6;
            color: white;
            border-color: #3B82F6;
        }

        /* 메인 컨텐츠 영역에 상단 여백 추가 (네비바 높이만큼) */
        .main .block-container {
            padding-top: 80px !important;
            margin-top: 0 !important;
        }

        /* ═══════════════════════════════════════════════════════════════ */
        /* 3. 사이드바 스타일 */
        /* ═══════════════════════════════════════════════════════════════ */
        [data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            background-color: #F8FAFC;
            border-right: 1px solid #E2E8F0;
            padding-top: 60px !important;
            margin-top: 0 !important;
        }

        /* 사이드바 숨기기 버튼 제거 */
        [data-testid="collapsedControl"] {
            display: none !important;
        }

        /* 사이드바 버튼 */
        div[data-testid="stSidebar"] button {
            background-color: white !important;
            border-radius: 12px !important;
            padding: 12px 20px !important;
            border: 1px solid #E2E8F0 !important;
            color: #475569 !important;
            font-weight: 600 !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            margin-bottom: 8px !important;
            text-align: left !important;
            display: flex;
            align-items: center;
        }

        div[data-testid="stSidebar"] button:hover {
            border-color: #3B82F6 !important;
            color: #3B82F6 !important;
            background-color: #EFF6FF !important;
            transform: translateX(3px);
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.1);
        }

        /* ═══════════════════════════════════════════════════════════════ */
        /* 4. 헤더 및 카드 스타일 */
        /* ═══════════════════════════════════════════════════════════════ */
        .tradenex-header {
    background: linear-gradient(90deg, #5B9BD5 0%, #4A8BC2 50%, #F8F9FA 100%);
    padding: 30px;
    border-radius: 16px;
    color: white;
    margin-bottom: 30px;
    box-shadow: 0 4px 6px rgba(91, 155, 213, 0.2);
}
        .tradenex-header h1 { color: white !important; margin: 0; font-size: 2.0rem !important; font-weight: 700 !important; }
        .tradenex-header p { color: #CBD5E1; margin-top: 8px; font-size: 1.0rem !important; }
        
       

        /* 5. 채팅창 스타일링 */
        .stChatMessage {
            background-color: transparent !important;
        }

        /* ═══════════════════════════════════════════════════════════════ */
        /* 6. Logistics 페이지 전용 스타일 */
        /* ═══════════════════════════════════════════════════════════════ */
        .sanction-alert {
            background-color: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #ffcdd2;
            font-weight: bold;
            margin-bottom: 15px;
            animation: pulse 2s infinite;
        }
        .confidence-high {
            background-color: #e8f5e9;
            color: #2e7d32;
            padding: 10px;
            border-radius: 5px;
            border-left: 5px solid #4caf50;
            font-size: 14px;
            margin: 10px 0;
        }
        .confidence-low {
            background-color: #fff8e1;
            color: #f57f17;
            padding: 10px;
            border-radius: 5px;
            border-left: 5px solid #ffca28;
            font-size: 14px;
            margin: 10px 0;
        }
        .fta-banner {
            background-color: #e3f2fd;
            color: #1565c0;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #90caf9;
            text-align: center;
            font-weight: bold;
            margin-top: 10px;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(255, 82, 82, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(255, 82, 82, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 82, 82, 0); }
        }
        .summary-card {
            background-color: #262730;
            padding: 15px;
            border-radius: 8px;
            border-left: 5px solid #ff4b4b;
            color: white;
            margin-bottom: 10px;
        }

        /* ═══════════════════════════════════════════════════════════════ */
        /* 7. Sales 페이지 전용 스타일 */
        /* ═══════════════════════════════════════════════════════════════ */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Pretendard:wght@300;400;600;700;900&display=swap');

        .main { background-color: #f8f9fb; }
        .stApp header { background-color: #1a1f36; }

        h1, h2, h3 {
            color: #1a1f36 !important;
            font-weight: 700 !important;
        }

        /* SIDEBAR - Sales 스타일 */
        .sb-container {
            background-color: #F8F9FA;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        }
        .sb-card {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .sb-divider {
            height: 1px;
            background: #E2E8F0;
            margin: 15px 0;
        }

        /* SECTION HEADER */
        .section-header {
            background: linear-gradient(135deg, #1a1f36 0%, #2d3348 100%);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            margin: 20px 0 15px 0;
            font-size: 16px;
            font-weight: 500;
            letter-spacing: 0.5px;
        }

        /* INFO BOX */
        .info-box {
            background: #e8f4f8;
            border-left: 4px solid #1a73e8;
            padding: 12px 16px;
            border-radius: 0 6px 6px 0;
            margin: 10px 0;
            font-size: 14px;
        }
        .success-box {
            background: #e6f4ea;
            border-left: 4px solid #34a853;
            padding: 12px 16px;
            border-radius: 0 6px 6px 0;
            margin: 10px 0;
        }

        /* CHART CARD */
        .chart-card {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .chart-header {
            font-size: 0.9rem;
            font-weight: 600;
            color: #64748B;
            margin-bottom: 8px;
        }
        .chart-value {
            font-size: 1.8rem;
            font-weight: 800;
            color: #0F172A;
            margin-bottom: 4px;
        }
        .chart-change {
            font-size: 0.85rem;
            margin-bottom: 12px;
        }
        .chart-comment {
            background: #F8F9FA;
            padding: 10px;
            border-radius: 6px;
            font-size: 0.85rem;
            color: #475569;
            margin-top: 10px;
        }

        /* NEWS CARD */
        .news-card {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 20px;
        }
        .news-header {
            font-size: 0.9rem;
            font-weight: 700;
            color: #64748B;
            border-bottom: 2px solid #0F172A;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .news-item {
            padding: 10px 0;
            border-bottom: 1px solid #F1F5F9;
        }
        .news-item:last-child {
            border-bottom: none;
        }
        .news-link {
            color: #2563EB;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            display: block;
            margin-bottom: 4px;
        }
        .news-link:hover {
            text-decoration: underline;
        }
        .news-meta {
            font-size: 0.75rem;
            color: #94A3B8;
        }

        /* BUYER CARD */
        .buyer-card {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
            border-left: 6px solid #2563EB;
        }
        .buyer-title {
            font-size: 1.4rem;
            font-weight: 800;
            color: #1E293B;
            margin-bottom: 8px;
        }
        .fin-badge {
            background: #F1F5F9;
            color: #475569;
            padding: 5px 10px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.85rem;
            margin-right: 6px;
        }

        /* MARGIN INFO */
        .margin-info-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin: 15px 0;
        }
        .profit-highlight {
            background: rgba(255,255,255,0.2);
            padding: 12px;
            border-radius: 8px;
            margin-top: 10px;
            font-size: 1.3rem;
            font-weight: 800;
            text-align: center;
        }

        /* MARGIN COMPACT CARD (Tab 2 우측 패널용) */
        .margin-compact-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 15px;
        }
        .margin-rate {
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .margin-benchmark {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        .margin-logic {
            font-size: 0.8rem;
            opacity: 0.8;
        }

        /* OFFER TRACKING TABLE (Tab 3용) */
        .offer-tracking-table {
            background: white;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #E2E8F0;
        }

        /* STEP INDICATOR */
        .step-wrapper {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 40px;
        }
        .step-item {
            padding: 10px 24px;
            border-radius: 50px;
            font-weight: 700;
            color: #94A3B8;
            background: white;
            border: 2px solid #E2E8F0;
            margin: 0 10px;
        }
        .step-item.active {
            background: #0F172A;
            color: white;
            border-color: #0F172A;
        }
        .step-line {
            flex-grow: 1;
            height: 3px;
            background: #E2E8F0;
            margin: 0 -15px;
            max-width: 50px;
        }

        /* FOOTER */
        .footer {
            text-align: center;
            padding: 20px;
            color: #94A3B8;
            font-size: 0.85rem;
            border-top: 1px solid #E2E8F0;
            margin-top: 40px;
        }
        </style>
    """, unsafe_allow_html=True)

def display_header(title, subtitle=""):
    st.markdown(f"""
        <div class="tradenex-header" style="background: linear-gradient(90deg, #5B9BD5 0%, #4A8BC2 30%, #8BB8DC 70%, #F8F9FA 100%) !important;">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def render_top_navbar(current_page=None):
    """상단 네비게이션 바 - 자동 페이지 감지 + 완전 고정"""
    
    # 현재 페이지 자동 감지
    if current_page is None:
        try:
            import streamlit.runtime.scriptrunner as scriptrunner
            ctx = scriptrunner.get_script_run_ctx()
            if ctx:
                script_path = ctx.script_path
                if "home.py" in script_path:
                    current_page = "home"
                elif "purchasing" in script_path:
                    current_page = "purchasing"
                elif "logistics" in script_path:
                    current_page = "logistics"
                elif "sale" in script_path:
                    current_page = "sales"
                else:
                    current_page = "home"
            else:
                current_page = "home"
        except:
            current_page = "home"
    
    # 네비바 HTML + CSS
    st.markdown(f"""
    <style>
    /* 고정 네비바 */
    .fixed-navbar {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 60px;
        background-color: #F8FAFC;
        border-bottom: 2px solid #E2E8F0;
        z-index: 999999;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        padding: 0 30px;
        gap: 15px;
    }}
    
    .fixed-navbar-logo {{
        font-size: 1.4rem;
        font-weight: 800;
        color: #1E293B;
        margin-right: 30px;
    }}
    
    .fixed-navbar-buttons {{
        display: flex;
        gap: 15px;
        margin-left: auto;
    }}
    
    .fixed-navbar-btn {{
        padding: 8px 20px;
        background-color: white;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        color: #475569;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s;
        text-decoration: none;
        display: inline-block;
    }}
    
    .fixed-navbar-btn:hover {{
        border-color: #3B82F6;
        color: #3B82F6;
        background-color: #EFF6FF;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);
    }}
    
    .fixed-navbar-btn.active {{
        background-color: #3B82F6;
        color: white;
        border-color: #3B82F6;
    }}
    
    /* 메인 컨텐츠 상단 여백 */
    .main .block-container {{
        padding-top: 80px !important;
    }}
    </style>
    
    <div class="fixed-navbar">
        <div class="fixed-navbar-logo">NexTrade ERP</div>
        <div class="fixed-navbar-buttons">
            <button class="fixed-navbar-btn {'active' if current_page == 'home' else ''}" onclick="window.location.href='/'">
                🏠 홈
            </button>
            <button class="fixed-navbar-btn {'active' if current_page == 'purchasing' else ''}" onclick="window.location.href='/purchasing_1'">
                📦 구매
            </button>
            <button class="fixed-navbar-btn {'active' if current_page == 'logistics' else ''}" onclick="window.location.href='/logistics_1'">
                🚚 물류
            </button>
            <button class="fixed-navbar-btn {'active' if current_page == 'sales' else ''}" onclick="window.location.href='/sale_1'">
                💼 영업
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_gradient_header():
    """그라데이션 헤더 박스 (#5B9BD5 블루 그라데이션)"""
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, #5B9BD5 0%, #4A8BC2 50%, #F8F9FA 100%);
        height: 80px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(91, 155, 213, 0.2);
    "></div>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        # =========================================================
        # 0. 로고 영역 (상단)
        # =========================================================
        st.markdown("""
        <div style='background: linear-gradient(135deg, #5B9BD5 0%, #4A8BC2 100%); 
                    padding: 20px; 
                    border-radius: 12px; 
                    margin-bottom: 20px; 
                    text-align: center;
                    border: 1px solid #4A8BC2;
                    box-shadow: 0 2px 4px rgba(91, 155, 213, 0.2);'>
            <div style='color: white; font-size: 1.5rem; font-weight: 800; letter-spacing: 2px;'>
                NexTrade
            </div>
            <div style='color: #E8F4F9; font-size: 0.75rem; margin-top: 5px; letter-spacing: 1px;'>
                ERP SYSTEM
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # =========================================================
        # 1. 로그인 정보 (구분선 추가)
        # =========================================================
        user_id = st.session_state.get('user_id', 'Guest')

        st.markdown(f"""
        <div style='background: white; padding:16px; border-radius:12px; margin-bottom:15px; border:2px solid #5B9BD5; box-shadow: 0 2px 4px rgba(91, 155, 213, 0.1);'>
            <div style='color:#334155; font-size:0.85rem; line-height:1.8; font-weight:400;'>
                <div style='margin-bottom:8px; padding-bottom:8px; border-bottom:1px solid #E2E8F0;'>
                    <span style='opacity:0.7;'>이름:</span> <span style='font-weight:600;'>{user_id}</span>
                </div>
                <div style='margin-bottom:8px; padding-bottom:8px; border-bottom:1px solid #E2E8F0;'>
                    <span style='opacity:0.7;'>직급:</span> <span style='font-weight:600;'>사원</span>
                </div>
                <div>
                    <span style='opacity:0.7;'>사번:</span> <span style='font-weight:600;'>213124134</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Logout", key="logout_btn", use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

        st.markdown("<div style='margin: 20px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)

        # =========================================================
        # 2. AI 챗봇
        # =========================================================
        st.markdown("### The System")
        st.caption("시스템이 당신의 무역 업무를 보조합니다.")

        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "시스템: 무엇을 도와드릴까요?"}]

        chat_container = st.container(height=300)
        with chat_container:
            for msg in st.session_state.messages:
                avatar = "🤖" if msg['role'] == "assistant" else "👤"
                st.chat_message(msg['role'], avatar=avatar).write(msg['content'])

        if prompt := st.chat_input("명령어 입력...", key="sidebar_chat"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            api_key = os.getenv("OPENAI_API_KEY")
            response = "시스템 오류: API 키가 없습니다."
            if api_key:
                try:
                    client = OpenAI(api_key=api_key)
                    completion = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": "You are a concise AI assistant for a trade system."}] + st.session_state.messages,
                        temperature=0.7
                    )
                    response = completion.choices[0].message.content
                except Exception as e:
                    response = f"오류: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

        # =========================================================
        # 3. 페이지 이동 버튼 (맨 아래)
        # =========================================================
        st.markdown("<div style='margin: 30px 0; border-top: 2px solid #E2E8F0;'></div>", unsafe_allow_html=True)
        st.markdown("### 📍 빠른 이동")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 홈", use_container_width=True, key="nav_home"):
                st.switch_page("home.py")
            if st.button("🚚 물류", use_container_width=True, key="nav_logistics"):
                st.switch_page("pages/logistics_1.py")
        with col2:
            if st.button("📦 구매", use_container_width=True, key="nav_purchasing"):
                st.switch_page("pages/purchasing_1.py")
            if st.button("💼 영업", use_container_width=True, key="nav_sales"):
                st.switch_page("pages/sale_1.py")