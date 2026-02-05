"""
Sales 페이지 탭 핸들러
- Tab 1: 시장조사 & 바이어 발굴
- Tab 2: 오퍼시트 생성 (자동 송부 기능 추가)
"""

import os
import io
import time
import random
import datetime
import zipfile
import streamlit as st
import pandas as pd
from docx import Document
import tempfile
import base64

# docx2pdf는 클라우드에서 작동하지 않음 (Microsoft Word 필요)
try:
    from docx2pdf import convert
    HAS_DOCX2PDF = True
except ImportError:
    HAS_DOCX2PDF = False

import subprocess
import shutil

def convert_docx_to_pdf_libreoffice(docx_path, output_dir):
    """LibreOffice를 사용한 DOCX -> PDF 변환 (클라우드용)"""
    try:
        libreoffice_path = shutil.which('libreoffice') or shutil.which('soffice')
        if not libreoffice_path:
            return None

        subprocess.run([
            libreoffice_path,
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            docx_path
        ], check=True, timeout=60)

        pdf_filename = os.path.basename(docx_path).replace('.docx', '.pdf')
        pdf_path = os.path.join(output_dir, pdf_filename)

        if os.path.exists(pdf_path):
            return pdf_path
        return None
    except Exception as e:
        print(f"LibreOffice 변환 오류: {e}")
        return None

# 모듈 import
from modules.sales.dashboard import fetch_dashboard_data, draw_candlestick_chart, generate_analysis
from modules.sales.buyer_search import fetch_buyer_list, generate_dummy_buyer
from modules.sales.translator import translate_offer_data, COUNTRIES
from modules.sales.offer_manager import initialize_offer_form, calculate_totals

@st.dialog("📢 [필독] 수출 성공을 위한 바이어 발굴 로드맵", width="large")
def show_buyer_guide():
    """바이어 검색 전 가이드 팝업"""
    
    st.markdown("""
    ### 🛑 잠깐! 무작정 검색부터 시작하고 계신가요?
    
    준비 없는 바이어 서칭은 **모래사장 위에서 바늘 찾기**와 같습니다.  
    아래의 체계적인 **7단계 프로세스**를 먼저 점검해보세요.  
    여러분의 바이어 매칭 성공률이 **200% 높아집니다!**
    """)
    
    st.divider()
    
    # STEP 1
    st.markdown("""
    #### 📍 STEP 1. 수출 물품 선정
    **"무엇을 팔 것인가?"**  
    시장성과 경쟁력을 갖춘 우리 회사의 확실한 주력 아이템(Hero Item)을 확정하세요.
    """)
    
    # STEP 2
    st.markdown("""
    #### 📍 STEP 2. HS 코드 및 수출 요건 확인
    **"수출 길을 뚫어라!"**  
    내 제품의 HS 코드를 정확히 분류하고, 관세율 및 필수 인증/규제 요건을 미리 점검해야 합니다.
    """)
    
    # STEP 3
    st.markdown("""
    #### 📍 STEP 3. 제품 심층 분석 (상품력 & 차별화)
    **"왜 우리 제품이어야 하는가?"**  
    경쟁사 대비 확실한 강점(USP)을 찾으세요. (가격, 성능, 품질, 디자인 등)
    """)
    
    # STEP 4
    st.markdown("""
    #### 📍 STEP 4. 목표 시장(공급 국가) 선정
    **"어디에 팔 것인가?"**  
    시장 규모, 성장성, 물류 접근성을 고려하여 최적의 타겟 국가를 선정합니다.
    """)
    
    # STEP 5
    st.markdown("""
    #### 📍 STEP 5. 해외 시장 정밀 조사
    **"적을 알고 나를 알면 백전백승!"**  
    타겟 국가의 유통 구조, 최신 트렌드, 경쟁사 현황을 심층적으로 파악합니다.
    """)
    
    # STEP 6
    st.markdown("""
    #### 📍 STEP 6. 바이어(Buyer) 발굴
    **"진짜 파트너를 찾아라!"**  
    B2B 플랫폼, 전시회, 무역관 등 다양한 채널을 통해 유력 바이어 리스트를 확보합니다.
    """)
    
    # STEP 7
    st.markdown("""
    #### 📍 STEP 7. 신용도 검증 (Credit Check)
    **"돌다리도 두들겨 보고!"**  
    거래 전 필수! 바이어의 재무 상태 및 평판을 조회하여 거래 리스크를 사전에 차단하세요.
    """)
    
    st.divider()
    
    st.success("✅ 위 7단계를 모두 점검하셨다면, 이제 본격적으로 바이어 발굴을 시작하세요!")
    
    if st.button("확인", type="primary", use_container_width=True):
        st.rerun()

def run_market_research():
    """Tab 1: 시장조사 & 바이어 발굴 (기존 Step 1-2 통합)"""

    st.markdown("## 시장 조사 & 바이어 발굴")

    # 대시보드 데이터 조회
    dash = fetch_dashboard_data()

    # Step 1: 품목/국가 입력
    c1, c2, c3, c4 = st.columns([2.5, 2.5, 2, 1.5], vertical_alignment="bottom")
    
    with c1:
        st.markdown("##### 수출 품목")
        product = st.text_input("product", placeholder="예: 마시는 샘물, 화장품", label_visibility="collapsed", key="input_product")
    with c2:
        st.markdown("##### 타겟 국가")
        country = st.text_input("country", placeholder="예: 몽골, 베트남, 브라질", label_visibility="collapsed", key="input_country")
    with c3:
        if st.button("시장 분석 및 바이어 찾기", type="primary", use_container_width=True):
            if product and country:
                st.session_state.target_product = product
                st.session_state.target_country = country
                with st.status("글로벌 데이터베이스 조회 중...", expanded=True) as s:
                    time.sleep(0.5)
                    s.update(label="완료!", state="complete", expanded=False)
                st.session_state.buyer_list = fetch_buyer_list(product, country)
                st.success(f"{len(st.session_state.buyer_list)}개 바이어 발견! 아래에서 선택하세요.")
                st.rerun()
            else:
                st.warning("품목과 국가를 모두 입력해주세요")
    with c4:
        if st.button("📢 검색 전 클릭 필수!", type="secondary", use_container_width=True):
            show_buyer_guide()

    st.markdown("<br>", unsafe_allow_html=True)

    # 대시보드 표시
    col1, col2, col3 = st.columns([1, 1, 1.3])

    with col1:
        ex_change = dash['exchange'].get('change', 0)
        ex_change_pct = dash['exchange'].get('change_pct', 0)
        color = "red" if ex_change < 0 else "green"

        st.markdown(f"""<div class="chart-card">
        <div class="chart-header">USD/KRW 환율</div>
        <div class="chart-value">{dash['exchange']['current']:,.1f} 원</div>
        <div class="chart-change" style="color: {color};">
            {'▼' if ex_change < 0 else '▲'} {abs(ex_change):.1f} ({abs(ex_change_pct):.2f}%)
        </div>
    </div>""", unsafe_allow_html=True)

        if not dash['exchange']['history'].empty:
            st.plotly_chart(draw_candlestick_chart(dash['exchange']['history']),
                          use_container_width=True, config={'displayModeBar': False})
            st.markdown(f"""<div class="chart-comment">{generate_analysis("exchange", ex_change_pct)}</div>""",
                   unsafe_allow_html=True)

    with col2:
        oil_change = dash['oil'].get('change', 0)
        oil_change_pct = dash['oil'].get('change_pct', 0)
        color = "red" if oil_change < 0 else "green"

        st.markdown(f"""<div class="chart-card">
        <div class="chart-header">WTI 원유</div>
        <div class="chart-value">{dash['oil']['current']:.2f} USD</div>
        <div class="chart-change" style="color: {color};">
            {'▼' if oil_change < 0 else '▲'} {abs(oil_change):.2f} ({abs(oil_change_pct):.2f}%)
        </div>
    </div>""", unsafe_allow_html=True)

        if not dash['oil']['history'].empty:
            st.plotly_chart(draw_candlestick_chart(dash['oil']['history']),
                          use_container_width=True, config={'displayModeBar': False})
            st.markdown(f"""<div class="chart-comment">{generate_analysis("oil", oil_change_pct)}</div>""",
                   unsafe_allow_html=True)

    with col3:
        st.markdown("""<div class="news-card">
        <div class="news-header">글로벌 무역 브리핑</div>
    """, unsafe_allow_html=True)

        for news in dash['news']:
            st.markdown(f"""<div class="news-item">
            <a href="{news.get('url', '#')}" class="news-link" target="_blank">{news['title']}</a>
            <div class="news-meta">{news['source']} • {news['date']}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Step 2: 바이어 리스트 (buyer_list가 있을 경우에만 표시)
    if 'buyer_list' in st.session_state and st.session_state.buyer_list:
        st.markdown("---")
        st.markdown(f"### {st.session_state.target_country} 유력 바이어 리스트")
        st.info("오퍼를 발송할 업체들을 왼쪽 체크박스로 선택해 주세요.")

        if 'selected_buyer_ids' not in st.session_state:
            st.session_state.selected_buyer_ids = []

        for b in st.session_state.buyer_list:
            with st.container():
                c0, c1 = st.columns([0.3, 5])

                with c0:
                    st.markdown("<div style='height:45px'></div>", unsafe_allow_html=True)
                    is_checked = st.checkbox("", key=f"check_{b['id']}",
                                           value=b['id'] in st.session_state.selected_buyer_ids)

                    if is_checked:
                        if b['id'] not in st.session_state.selected_buyer_ids:
                            st.session_state.selected_buyer_ids.append(b['id'])
                    else:
                        if b['id'] in st.session_state.selected_buyer_ids:
                            st.session_state.selected_buyer_ids.remove(b['id'])

                with c1:
                    st.markdown(f"""
                        <div class="buyer-card">
                            <div class="buyer-title">{b['Name']}</div>
                            <div style="margin-bottom:8px;">
                                <span class="fin-badge">{b['Business']}</span>
                                <span class="fin-badge">{b.get('Revenue', 'N/A')}</span>
                            </div>
                            <div style="font-size:0.95rem; color:#334155; margin-bottom:5px;">{b['Desc']}</div>
                            <div style="color:#2563EB; font-weight:600;">{b['Email']}</div>
                        </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("추가 바이어 정보 검색하기", use_container_width=True):
                with st.spinner("탐색 중..."):
                    time.sleep(1)
                    new_buyers = []
                    for i in range(5):
                        new_buyers.append(generate_dummy_buyer(
                            st.session_state.target_product,
                            st.session_state.target_country,
                            len(st.session_state.buyer_list) + 100 + i
                        ))
                    st.session_state.buyer_list.extend(new_buyers)
                    st.rerun()

        with col_btn2:
            selected_count = len(st.session_state.selected_buyer_ids)
            if st.button(f"{selected_count}개 업체 선택 완료", type="primary", use_container_width=True):
                if selected_count > 0:
                    st.session_state.selected_buyers_full = [
                        b for b in st.session_state.buyer_list
                        if b['id'] in st.session_state.selected_buyer_ids
                    ]
                    st.success(f"{selected_count}개 업체 선택 완료! '오퍼시트 생성' 탭으로 이동하세요.")
                else:
                    st.warning("최소 한 개 이상의 업체를 선택해 주세요.")


def run_offer_generator():
    """Tab 2: 오퍼시트 생성"""
    
    # ========== [추가] 함수 안에서 import ==========
    from modules.sales.doc_maker import create_offer_sheet
    
    st.markdown("## 오퍼시트 생성")

    # API KEY 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.markdown('<div class="info-box">✅ <b>OPENAI_API_KEY</b> 감지됨 — 번역 기능 사용 가능</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">⚠️ <b>OPENAI_API_KEY</b>가 없습니다. 영문 전용으로 동작합니다.</div>',
                    unsafe_allow_html=True)

    # 세션 상태 초기화
    if "num_items" not in st.session_state:
        st.session_state.num_items = 3

    # Prefill 처리
    selected_buyers = st.session_state.get("selected_buyers_full", [])
    is_multiple = len(selected_buyers) > 1

    default_buyer_company = ""
    default_address = ""

    if is_multiple:
        buyer_names = ", ".join([f"**{b['Name']}**" for b in selected_buyers])
        st.success(f"발송 대상 업체 ({len(selected_buyers)}곳): {buyer_names}")
        st.info("생성 버튼 클릭 시 각 업체의 정보가 담긴 서류가 개별적으로 자동 생성됩니다.")
    elif selected_buyers:
        default_buyer_company = selected_buyers[0].get("Name", "")
        default_address = selected_buyers[0].get("Email", "")

    # 2-Column 레이아웃 (왼쪽: 폼, 우측: 마진율 & 요약)
    col_left, col_right = st.columns([2, 1])

    # === 우측 패널 ===
    with col_right:
        # 마진율 카드 (컴팩트)
        st.markdown("#### 마진율 설정")

        # 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(current_dir))
        margin_file = os.path.join(root_dir, "data", "sales", "margin.csv")
        df_margin = pd.read_csv(margin_file)

        category_options = df_margin['Category_Name'].tolist()
        selected_category = st.selectbox("카테고리", category_options, label_visibility="collapsed", key="margin_category_select")

        selected_row = df_margin[df_margin['Category_Name'] == selected_category].iloc[0]
        margin_rate = selected_row['Margin_Rate']

        # 컴팩트한 정보 표시
        st.markdown(f"""
        <div class="margin-compact-card">
            <div class="margin-rate">{margin_rate*100:.0f}%</div>
            <div class="margin-benchmark">{selected_row['Benchmark_Company']}</div>
            <div class="margin-logic">{selected_row['Logic_Summary']}</div>
        </div>
        """, unsafe_allow_html=True)

        # 행 개수 조절 (number_input)
        st.markdown("#### 상품 행 개수")
        num_items = st.number_input(
            "Items",
            min_value=1,
            max_value=20,
            value=st.session_state.num_items,
            label_visibility="collapsed",
            key="num_items_input"
        )
        if num_items != st.session_state.num_items:
            st.session_state.num_items = num_items
            st.rerun()

    # === 왼쪽 패널 ===
    with col_left:
        # 기본 정보 (판매자 정보)
        st.markdown('<div class="section-header">기본 정보 (Basic Info)</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            seller_name = st.text_input("Seller Name", value="JJimDak.CO.", placeholder="Company Name")
            address_attn = st.text_input("Address & Attn", value="513, Yeongdong-daero, Gangnam-gu, Seoul", placeholder="Full Address")
        with col2:
            seller_email = st.text_input("Contact Email", value="sales@jjimdak.co.kr", placeholder="email@company.com")
            date_val = st.date_input("Date", value=datetime.date.today())

        # Offer No는 자동 생성
        offer_no = f"NXT-{date_val.strftime('%Y%m%d')}-{random.randint(100, 999)}"

        # 바이어 정보
        if is_multiple:
            messrs = "Mr./Ms."
            buyer_company = "[Multiple Buyers]"
        else:
            messrs = "Mr./Ms."
            buyer_company = default_buyer_company if default_buyer_company else "Buyer Company"

        # 거래 조건
        st.markdown('<div class="section-header">거래 조건 (Trade Terms)</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            origin = st.text_input("Origin (원산지)", placeholder="Republic of Korea")
            shipment = st.text_input("Shipment (선적)", placeholder="Within 30 days after L/C")
            loading_port = st.text_input("Loading Port", placeholder="Busan, Korea")
        with col2:
            destination = st.text_input("Destination", placeholder="Ulaanbaatar, Mongolia")
            payment = st.text_input("Payment", placeholder="Irrevocable L/C at sight")
            packing = st.text_input("Packing", placeholder="Standard export packing")
        with col3:
            insurance = st.text_input("Insurance", placeholder="Covered by seller, 110%")
            inspection = st.text_input("Inspection", placeholder="SGS at loading port")
            validity = st.text_input("Validity", placeholder="30 days from date")

        # 상품 정보
        st.markdown('<div class="section-header">상품 정보</div>', unsafe_allow_html=True)
        st.caption("상품 개수를 우측 컨트롤에서 조정하세요")

        items = []

        hcols = st.columns([0.5, 3, 1.5, 1.5, 1.5])
        hcols[0].markdown("**No.**")
        hcols[1].markdown("**Description**")
        hcols[2].markdown("**Quantity**")
        hcols[3].markdown("**원가 (Cost)**")
        hcols[4].markdown("**판매가 (Price)**")

        total_cost = 0.0
        total_revenue = 0.0

        for i in range(st.session_state.num_items):
            cols = st.columns([0.5, 3, 1.5, 1.5, 1.5])
            no = cols[0].text_input(f"no_{i}", value=str(i + 1), label_visibility="collapsed", key=f"no_{i}")
            desc = cols[1].text_input(f"desc_{i}", placeholder="Product description", label_visibility="collapsed", key=f"desc_{i}")
            qty = cols[2].text_input(f"qty_{i}", placeholder="1,000 PCS", label_visibility="collapsed", key=f"qty_{i}")

            cost_price = cols[3].text_input(f"cost_{i}", placeholder="5.00", label_visibility="collapsed", key=f"cost_{i}")

            auto_selling_price = ""
            item_cost = 0.0
            item_revenue = 0.0

            try:
                if cost_price:
                    cost = float(cost_price.replace(",", ""))
                    selling = cost * (1 + margin_rate)
                    auto_selling_price = f"{selling:,.2f}"

                    q = float(qty.replace(",", "")) if qty else 0
                    if q > 0:
                        item_cost = cost * q
                        item_revenue = selling * q
                        total_cost += item_cost
                        total_revenue += item_revenue
            except ValueError:
                pass

            selling_price = cols[4].text_input(
                f"sell_{i}",
                value=auto_selling_price,
                placeholder="자동 계산",
                label_visibility="collapsed",
                key=f"sell_{i}"
            )

            items.append({
                "no": no,
                "description": desc,
                "quantity": qty,
                "unit_price": selling_price,
                "amount": f"{item_revenue:,.2f}" if item_revenue > 0 else ""
            })

        # 분쟁 해결 조항
        st.markdown('<div class="section-header">⚖️ 분쟁 해결 조항 (Dispute Resolution)</div>', unsafe_allow_html=True)

        c_legal, c_law = st.columns([1.5, 1])

        with c_legal:
            legal_method = st.radio(
                "해결 방식 (Method)", 
                ["Arbitration (국제 중재)", "Litigation (법원 소송)"], 
                horizontal=True
            )
            
            if "Arbitration" in legal_method:
                dispute_detail = st.text_input("중재 기관", value="KCAB, Seoul, Korea")
                dispute_full_text = f"All disputes shall be settled by Arbitration in {dispute_detail}."
            else:
                dispute_detail = st.text_input("관할 법원", value="Seoul Central District Court")
                dispute_full_text = f"All disputes shall be settled by Litigation at {dispute_detail}."

        with c_law:
            gov_law = st.text_input("준거법 (Governing Law)", value="Laws of Republic of Korea")

        # 번역 설정
        st.markdown('<div class="section-header">번역 설정</div>', unsafe_allow_html=True)

        country_options = [f"{info['flag']} {country}" for country, info in COUNTRIES.items()]
        selected_display = st.selectbox("목표 국가 선택", country_options, index=0)

        selected_country = selected_display.split(" ", 1)[1] if " " in selected_display else selected_display
        target_language = COUNTRIES[selected_country]["language"]

        if target_language:
            st.success(f"✅ 생성될 서류: **영어 + {target_language}** (2개 버전)")
        else:
            st.info("생성될 서류: **영어** (1개 버전)")

        

    # === 우측 패널 - 요약 메트릭 ===
    with col_right:
        # 이익 계산
        total_profit = total_revenue - total_cost
        profit_rate = (total_profit / total_cost * 100) if total_cost > 0 else 0

        st.markdown("#### 견적 요약")
        st.metric("총 원가", f"${total_cost:,.2f}")
        st.metric("총 판매가", f"${total_revenue:,.2f}")
        st.metric("예상 이익", f"${total_profit:,.2f}")
        st.metric("적용 마진율", f"{margin_rate*100:.0f}%", delta=f"{profit_rate:.1f}%")

    # === 생성 버튼 ===
    total_amount_input = f"{total_revenue:,.2f}" if total_revenue > 0 else ""

    st.markdown("---")
    
    # ★★★ [미리보기 섹션] ★★★
    st.markdown("### 👀 서류 미리보기")

    if st.button("🔍 미리보기 생성", use_container_width=True, type="primary"):
        with st.spinner("미리보기 생성 중..."):
            try:
                # 미리보기용 데이터 준비
                preview_target = selected_buyers[0] if selected_buyers else {"Name": buyer_company, "Email": address_attn}
                
                preview_form_data = {
                    "seller_name": seller_name,
                    "seller_addr": address_attn,
                    "seller_email": seller_email,
                    "buyer_company": preview_target["Name"],
                    "address_attn": preview_target.get("Email", address_attn),
                    "offer_no": offer_no,
                    "date": date_val.strftime("%B %d, %Y"),
                    "origin": origin or "Republic of Korea",
                    "shipment": shipment or "Within 30 days",
                    "loading_port": loading_port or "Busan, Korea",
                    "destination": destination or "TBD",
                    "payment": payment or "L/C at sight",
                    "packing": packing or "Standard export packing",
                    "insurance": insurance or "110% CIF",
                    "validity": validity or "30 days",
                    "dispute_resolution": dispute_full_text,
                    "governing_law": gov_law or "Laws of Republic of Korea",
                    "total_amount": total_amount_input,
                }
                
                preview_labels = None
                preview_items = items
                
                # 번역이 필요한 경우 처리
                if target_language:
                    translated = translate_offer_data(preview_form_data, items, target_language)
                    if translated:
                        preview_labels = translated.get('labels', None)
                        
                        # 번역된 form_data로 업데이트
                        preview_form_data = {
                            "seller_name": seller_name,
                            "seller_addr": address_attn,
                            "seller_email": seller_email,
                            "buyer_company": translated['values'].get('buyer_company', preview_target['Name']),
                            "address_attn": translated['values'].get('address_attn', preview_target.get("Email", "")),
                            "offer_no": translated['values'].get('offer_no', offer_no),
                            "date": translated['values'].get('date', date_val.strftime("%B %d, %Y")),
                            "origin": translated['values'].get('origin', origin),
                            "shipment": translated['values'].get('shipment', shipment),
                            "loading_port": translated['values'].get('loading_port', loading_port),
                            "destination": translated['values'].get('destination', destination),
                            "payment": translated['values'].get('payment', payment),
                            "packing": translated['values'].get('packing', packing),
                            "insurance": translated['values'].get('insurance', insurance),
                            "validity": translated['values'].get('validity', validity),
                            "dispute_resolution": translated['values'].get('arbitration', dispute_full_text),
                            "governing_law": translated['values'].get('governing_law', gov_law),
                            "total_amount": translated['values'].get('total_amount', total_amount_input),
                        }
                        
                        # 번역된 items 생성
                        preview_items = []
                        for trans_item in translated.get('items', []):
                            preview_items.append({
                                "no": trans_item.get('no', ''),
                                "description": trans_item.get('description', ''),
                                "quantity": trans_item.get('quantity', ''),
                                "unit_price": trans_item.get('unit_price', ''),
                                "amount": trans_item.get('amount', '')
                            })
                
                # Word 문서 생성
                doc_buf = create_offer_sheet(preview_form_data, preview_items, signature_img=None, labels=preview_labels)

                # 세션에 Word 파일 저장
                st.session_state['preview_docx'] = doc_buf.getvalue()
                lang_suffix = f"_{target_language}" if target_language else "_EN"
                st.session_state['preview_filename'] = f"Preview_OfferSheet_{offer_no}{lang_suffix}"

                # PDF 변환 (docx2pdf 또는 LibreOffice 사용)
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_docx:
                        tmp_docx.write(doc_buf.getvalue())
                        docx_path = tmp_docx.name

                    output_dir = os.path.dirname(docx_path)

                    if HAS_DOCX2PDF:
                        # 로컬: docx2pdf 사용
                        pdf_path = docx_path.replace('.docx', '.pdf')
                        convert(docx_path, pdf_path)
                    else:
                        # 클라우드: LibreOffice 사용
                        pdf_path = convert_docx_to_pdf_libreoffice(docx_path, output_dir)

                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, 'rb') as f:
                            st.session_state['preview_pdf'] = f.read()
                        os.unlink(pdf_path)
                    else:
                        st.session_state['preview_pdf'] = None

                    os.unlink(docx_path)
                except Exception as e:
                    print(f"PDF 변환 오류: {e}")
                    st.session_state['preview_pdf'] = None

                st.success("✅ 미리보기 생성 완료!")
                
            except Exception as e:
                st.error(f"미리보기 생성 실패: {e}")
                st.exception(e)

    # PDF 미리보기 표시 (로컬에서만 가능)
    if 'preview_pdf' in st.session_state and st.session_state['preview_pdf']:
        st.markdown("---")
        st.markdown("#### 📄 문서 미리보기")

        # PDF를 base64로 인코딩하여 iframe으로 표시
        base64_pdf = base64.b64encode(st.session_state['preview_pdf']).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

        st.markdown("---")
    elif 'preview_docx' in st.session_state:
        st.markdown("---")
        st.info("💡 PDF 미리보기는 로컬 환경에서만 지원됩니다. Word 파일을 다운로드하세요.")
        
        # 다운로드 버튼들
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 PDF 다운로드",
                data=st.session_state['preview_pdf'],
                file_name=f"{st.session_state.get('preview_filename', 'Preview')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="secondary"
            )
        with col2:
            st.download_button(
                label="📥 Word 다운로드",
                data=st.session_state['preview_docx'],
                file_name=f"{st.session_state.get('preview_filename', 'Preview')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                type="secondary"
            )

    st.markdown("---")
    
    # 요약 정보 배지
    st.markdown(f"""
    <div style="background-color:#E3F2FD; padding:12px; border-radius:8px; margin-bottom:15px; border:1px solid #90CAF9;">
        <div style="display:flex; justify-content:space-around; flex-wrap:wrap; gap:10px;">
            <div style="color:#1565C0; font-size:0.9rem; font-weight:bold;">
                💵 Total: ${total_revenue:,.2f}
            </div>
            <div style="color:#1565C0; font-size:0.9rem; font-weight:bold;">
                📦 Items: {len([i for i in items if i.get('description')])}
            </div>
            <div style="color:#1565C0; font-size:0.9rem; font-weight:bold;">
                🎯 Margin: {margin_rate*100:.0f}%
            </div>
            <div style="color:#1565C0; font-size:0.9rem; font-weight:bold;">
                📈 Profit: ${total_profit:,.2f}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 작성 Offer Sheet 다운로드 버튼
    if st.button("작성 Offer Sheet 다운로드", use_container_width=True, type="primary"):
        # ... (기존 코드 그대로, 들여쓰기만 맞춤)
        targets = selected_buyers if selected_buyers else [{"Name": buyer_company, "Email": address_attn}]

        zip_buffer = io.BytesIO()

        with st.spinner("서류 생성 중..."):
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zf:
                for target in targets:
                    current_form_data = {
                        "seller_name": seller_name,
                        "seller_addr": address_attn,
                        "seller_email": seller_email,
                        "buyer_company": target["Name"],
                        "address_attn": target.get("Email", ""),
                        "offer_no": offer_no,
                        "date": date_val.strftime("%B %d, %Y"),
                        "origin": origin,
                        "shipment": shipment,
                        "loading_port": loading_port,
                        "destination": destination,
                        "payment": payment,
                        "packing": packing,
                        "insurance": insurance,
                        "validity": validity,
                        "dispute_resolution": dispute_full_text,
                        "governing_law": gov_law,
                        "total_amount": total_amount_input,
                    }

                    # ========== [1] 영어 파일 생성 (항상) ==========
                    en_buf = create_offer_sheet(current_form_data, items, signature_img=None)
                    zf.writestr(f"OfferSheet_{target['Name']}_EN.docx", en_buf.getvalue())

                    # ========== [2] 번역 파일 생성 (선택 시) ==========
                    if target_language:
                        translated = translate_offer_data(current_form_data, items, target_language)
                        if translated:
                            # 번역된 form_data 생성
                            translated_form_data = {
                                "seller_name": seller_name,
                                "seller_addr": address_attn,
                                "seller_email": seller_email,
                                "buyer_company": translated['values'].get('buyer_company', target['Name']),
                                "address_attn": translated['values'].get('address_attn', target.get("Email", "")),
                                "offer_no": translated['values'].get('offer_no', offer_no),
                                "date": translated['values'].get('date', date_val.strftime("%B %d, %Y")),
                                "origin": translated['values'].get('origin', ''),
                                "shipment": translated['values'].get('shipment', ''),
                                "loading_port": translated['values'].get('loading_port', ''),
                                "destination": translated['values'].get('destination', ''),
                                "payment": translated['values'].get('payment', ''),
                                "packing": translated['values'].get('packing', ''),
                                "insurance": translated['values'].get('insurance', ''),
                                "validity": translated['values'].get('validity', ''),
                                "dispute_resolution": translated['values'].get('arbitration', dispute_full_text),
                                "governing_law": translated['values'].get('governing_law', gov_law),
                                "total_amount": translated['values'].get('total_amount', total_amount_input),
                            }
                            
                            # 번역된 items 생성
                            translated_items = []
                            for trans_item in translated.get('items', []):
                                translated_items.append({
                                    "no": trans_item.get('no', ''),
                                    "description": trans_item.get('description', ''),
                                    "quantity": trans_item.get('quantity', ''),
                                    "unit_price": trans_item.get('unit_price', ''),
                                    "amount": trans_item.get('amount', '')
                                })
                            
                            # 번역된 라벨 추출
                            translated_labels = translated.get('labels', None)
                            
                            # 전문 양식으로 번역 파일 생성 (라벨 포함!)
                            tr_buf = create_offer_sheet(translated_form_data, translated_items, signature_img=None, labels=translated_labels)
                            zf.writestr(f"OfferSheet_{target['Name']}_{target_language}.docx", tr_buf.getvalue())

        zip_buffer.seek(0)
        st.download_button(
            label="📥 Offer Sheet 다운로드 (ZIP)",
            data=zip_buffer.getvalue(),
            file_name=f"Offers_{date_val.strftime('%Y%m%d')}.zip",
            mime="application/zip",
            use_container_width=True,
            key="download_offer_zip"
        )
        st.success("✅ 서류 생성 완료! 위 버튼을 눌러 다운로드하세요.")
    
    # ★★★★★ [자동 송부 기능 추가] ★★★★★
    st.markdown("---")
    st.markdown("### 📧 Offer Sheet 자동 송부")
    
    # 선택된 바이어 정보 가져오기
    selected_buyers_for_send = st.session_state.get('selected_buyers_full', [])
    
    if selected_buyers_for_send:
        st.success(f"✅ {len(selected_buyers_for_send)}개 바이어가 선택되었습니다.")
        
        for buyer in selected_buyers_for_send:
            buyer_name = buyer.get('Name', '선택된 바이어')
            buyer_email = buyer.get('Email', 'N/A')
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{buyer_name}** ({buyer_email})")
            with col2:
                if st.button(f"📧 송부", key=f"send_{buyer.get('id', 0)}", type="primary", use_container_width=True):
                    # 송부 완료 알림
                    st.success(f"✅ **{buyer_name}** 에 Offer Sheet를 송부하였습니다!")
                    st.balloons()
                    
                    # 상세 정보 표시
                    with st.expander("📬 송부 상세 정보", expanded=True):
                        st.write(f"**수신 회사:** {buyer_name}")
                        st.write(f"**수신 이메일:** {buyer_email}")
                        st.write(f"**송부 일시:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**Offer No:** {offer_no}")
                        st.write(f"**첨부 파일:** OfferSheet_{buyer_name}_{datetime.date.today().strftime('%Y%m%d')}.zip")
    else:
        st.warning("⚠️ 선택된 바이어가 없습니다.")
        st.info("💡 **Tab1 (시장조사 & 바이어)**에서 바이어를 먼저 선택해주세요.")


def run_document_center():
    """Tab 3: 서류 작성 & 추적"""

    st.markdown("## 서류 작성 & 추적")

    # 무역 서류 생성
    st.markdown("### 최종 무역 서류 작성 (CI/PL)")

    with st.container():
        st.markdown('<div class="sb-container">', unsafe_allow_html=True)
        st.markdown("**상업 송장 (Commercial Invoice) 및 포장 명세서 (Packing List)**")
        c1, c2 = st.columns(2)
        from datetime import date
        inv_no = c1.text_input("Invoice No.", f"INV-{date.today().strftime('%Y%m%d')}")
        lc_no = c2.text_input("L/C No.", "LC-00000000")
        st.markdown("---")
        if st.button("전체 서류 일괄 생성", type="primary", use_container_width=True):
            doc = Document()
            doc.add_heading(f"INVOICE {inv_no}", 0)
            buf = io.BytesIO()
            doc.save(buf)
            buf.seek(0)
            st.download_button("서류 다운로드", buf, "Trade_Docs.docx")
            st.success("생성 완료")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 발송 내역 추적
    st.markdown("### 발송 내역 추적")

    if 'sent_offers' not in st.session_state:
        st.session_state.sent_offers = []

    if not st.session_state.sent_offers:
        st.info("아직 발송된 오퍼가 없습니다.")
    else:
        df = pd.DataFrame(st.session_state.sent_offers)

        # 상태별 필터
        status_filter = st.multiselect(
            "상태 필터",
            ["Draft", "Sent", "Viewed", "Accepted", "Rejected"],
            default=["Sent", "Viewed"]
        )

        if status_filter:
            filtered_df = df[df['status'].isin(status_filter)]
        else:
            filtered_df = df

        # 편집 가능한 데이터프레임
        edited_df = st.data_editor(
            filtered_df,
            column_config={
                "status": st.column_config.SelectboxColumn(
                    "상태",
                    options=["Draft", "Sent", "Viewed", "Accepted", "Rejected"],
                    required=True
                ),
                "date": st.column_config.DateColumn("발송일"),
                "buyer": st.column_config.TextColumn("바이어"),
            },
            hide_index=True,
            use_container_width=True
        )

        # 변경사항 저장
        if st.button("변경사항 저장"):
            st.session_state.sent_offers = edited_df.to_dict('records')
            st.success("저장 완료!")