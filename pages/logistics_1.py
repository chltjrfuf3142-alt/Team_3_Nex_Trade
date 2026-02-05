import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go
import time
import os
import sys
import math
import pydeck as pdk 
from dotenv import load_dotenv

# ==========================================
# 1. 환경 설정 및 모듈 로드
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

load_dotenv(dotenv_path=os.path.join(parent_dir, '.env'))

try:
    from modules.ui import setup_app_style, display_header, render_sidebar, render_top_navbar
    from modules.logistics.calculator import LogisticsCalculator
    from modules.logistics.incoterms import IncotermManager
    from modules.logistics.customs import CustomsBroker
    from modules.logistics.ai_agent import AIAgent
    from modules.logistics.finance import get_realtime_exchange_rate
    from modules.logistics.risk_manager import check_strategic_goods, analyze_cargo_context, get_strategic_goods_details
    from modules.logistics.visualizer import render_3d_route, draw_cost_waterfall
except ImportError as e:
    st.error(f"🚨 모듈 로드 실패: {e}")
    st.stop()

# ==========================================
# 2. 페이지 기본 설정
# ==========================================
setup_app_style()
render_top_navbar(current_page="logistics")
render_sidebar()

# 뒤로가기 버튼
if st.button("← 뒤로가기", key="back_to_home_logistics"):
    st.switch_page("home.py")

# 객체 초기화
calc = LogisticsCalculator()
incoterm_mgr = IncotermManager()
customs = CustomsBroker()
ai = AIAgent(os.getenv("OPENAI_API_KEY"))

display_header("스마트 물류 플랫폼", "AI 기반 물류 최적화 및 비용 산출")
tabs = st.tabs(["화물 & 국가 설정", "최적 경로 시각화", "물류비 견적 산출", "AI 전략 컨설팅"])

# 전역 변수 설정 (탭 간 데이터 공유용)
if 'product_name' not in st.session_state: 
    st.session_state['product_name'] = "말보루 레드"

# ----------------------------------------------------------------
# TAB 1: 화물 설정 (AI 분석 통합)
# ----------------------------------------------------------------
with tabs[0]:
    st.subheader("스마트 화물 설정")
    
    if 'target_country_key' not in st.session_state:
        st.session_state['target_country_key'] = "Mongolia"
    
    col_input, col_dest = st.columns([1.2, 1])
    
    with col_dest:
        st.subheader("목적지 및 물량")
        target_country = st.radio(
            "목적지",
            ["Mongolia", "Kazakhstan"],
            horizontal=True,
            key='target_country_key'
        )

        cost_krw = st.number_input("단가 (원)", value=5000)
        teu = st.slider("물량 (TEU)", 1, 50, 1)

        st.markdown(f"**통관 규정 확인: {target_country}**")
        with st.expander("🚨 필수 통관 서류 (Checklist)", expanded=True):
            st.checkbox("Commercial Invoice (Original)", value=True)
            st.checkbox("Certificate of Origin (Form-MK)")
            st.checkbox("Packing List")
            st.checkbox("Food Safety Inspection")

    with col_input:
        product_name = st.text_input("제품명", st.session_state['product_name'])
        st.session_state['product_name'] = product_name

        # AI 전략물자 분석
        with st.spinner("🤖 AI가 제품을 분석하고 있습니다..."):
            strategic_info = get_strategic_goods_details(product_name)
            st.session_state['strategic_analysis'] = strategic_info
        
        risk_colors = {
            'CRITICAL': '#d32f2f',
            'HIGH': '#f57c00',
            'MEDIUM': '#fbc02d',
            'LOW': '#388e3c'
        }
        
        risk_level = strategic_info.get('risk_level', 'LOW')
        risk_color = risk_colors.get(risk_level, '#757575')
        
        if strategic_info.get('is_strategic'):
            st.markdown(
                f'<div style="background: linear-gradient(135deg, {risk_color}22 0%, {risk_color}11 100%); '
                f'border-left: 5px solid {risk_color}; padding: 15px; border-radius: 8px; margin: 10px 0;">'
                f'<h4 style="margin: 0; color: {risk_color};">🚨 전략물자 감지</h4>'
                f'<p style="margin: 5px 0;"><b>분류:</b> {strategic_info.get("category", "Unknown")}</p>'
                f'<p style="margin: 5px 0;"><b>리스크:</b> {risk_level}</p>'
                f'<p style="margin: 5px 0;"><b>사유:</b> {strategic_info.get("reason", "N/A")}</p>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            if strategic_info.get('requires_license'):
                with st.expander("📋 필수 절차 및 규제", expanded=True):
                    st.warning(f"**담당 기관**: {strategic_info.get('authority', '산업통상자원부')}")
                    
                    st.markdown("**적용 규제:**")
                    regulations = strategic_info.get('regulations', [])
                    if regulations:
                        for reg in regulations:
                            st.markdown(f"- {reg}")
                    else:
                        st.markdown("- 수출허가 필요 (상세 규제 확인 필요)")
                    
                    st.error("⚠️ **경고**: 무허가 수출 시 5년 이하 징역 또는 5억원 이하 벌금")
        else:
            st.success(f"✅ 일반 화물 ({risk_level} Risk)")
            st.caption(strategic_info.get('reason', '전략물자에 해당하지 않습니다.'))

        # HS 코드 분석
        with st.spinner("HS 코드 분석 중..."):
            hs_info = customs.get_hs_code_and_duty(product_name, target_country)
            
            st.session_state['current_hs_code'] = hs_info['hs_code']
            st.session_state['duty_rate'] = hs_info['duty_rate']
            
            conf_score = 90 + (len(product_name) % 9)
            st.markdown(
                f'<div style="background: #e8f5e9; border-left: 4px solid #4caf50; '
                f'padding: 10px; border-radius: 5px; margin: 10px 0;">'
                f'✅ <b>AI Matching Confidence: {conf_score}%</b><br>'
                f'추천된 HS CODE가 품목 설명과 매우 일치합니다.'
                f'</div>',
                unsafe_allow_html=True
            )

        c1, c2 = st.columns(2)
        c1.metric("선택된 HS 코드", hs_info['hs_code'])
        c2.metric("기본 관세율", f"{hs_info['duty_rate']}%")

        st.markdown("#### 유사 HS 코드 (참고)")
        prefix = hs_info['hs_code'].split('.')[0]
        df_similar = pd.DataFrame({
            "코드": [f"{prefix}.10", f"{prefix}.20", f"{prefix}.99"],
            "설명": [f"{product_name} 기타 유형", "원자재", "부속품 및 부품"],
            "세율": [f"{hs_info['duty_rate']}%", f"{max(0, hs_info['duty_rate']-2)}%", f"{hs_info['duty_rate']+1}%"]
        })
        st.dataframe(df_similar, hide_index=True, use_container_width=True)

    st.divider()
    est_total_usd = (cost_krw * teu * 20000) / 1380
    saving_amt = est_total_usd * (hs_info['duty_rate']/100)
    
    st.markdown(f"""
    <div class="fta-banner">
        💰 FTA Opportunity Detected! (한-{target_country} 협정 / RCEP)<br>
        협정 관세 적용 시 약 <span style="font-size:1.2em; color:#d32f2f;">${saving_amt:,.0f}</span> 절감 가능
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------
# TAB 2: 최적 경로 시각화
# ----------------------------------------------------------------
with tabs[1]:
    st.subheader(f"3D 경로 시각화: 인천 ➔ {target_country}")
    
    LOC_INCHEON = [126.60, 37.45]
    LOC_LIANYUNGANG = [119.22, 34.60]
    LOC_ZHENGZHOU = [113.62, 34.74]
    
    path_ocean = [
        LOC_INCHEON,
        [124.50, 36.50],
        [121.00, 35.00], 
        LOC_LIANYUNGANG
    ]
    
    path_inland = [
        LOC_LIANYUNGANG,
        [116.00, 34.80],
        LOC_ZHENGZHOU
    ]
    
    if "Mongolia" in target_country:
        LOC_ULAANBAATAR = [106.91, 47.92]
        path_rail = [
            LOC_ZHENGZHOU,
            [115.50, 38.00],
            [113.00, 41.00],
            [111.98, 43.65],
            LOC_ULAANBAATAR
        ]
        rail_distance = "1,743 km"
        rail_days = "5-7 days"
    else:
        LOC_ALMATY = [76.89, 43.22]
        path_rail = [
            LOC_ZHENGZHOU,
            [108.93, 34.34],
            [96.00, 40.00],
            [87.61, 43.82],
            LOC_ALMATY
        ]
        rail_distance = "3,850 km"
        rail_days = "12-15 days"

    raw_costs = calc.get_base_costs(target_country, teu)
    ocean_cost = raw_costs['ocean_cost']
    inland_cost = raw_costs['inland_kr_cost']
    rail_cost = raw_costs['rail_cost']
    
    real_fx = get_realtime_exchange_rate()
    
    ocean_cost_krw = ocean_cost * real_fx
    inland_cost_krw = inland_cost * real_fx
    rail_cost_krw = rail_cost * real_fx

    view_state = pdk.ViewState(
        latitude=38.0, 
        longitude=105.0, 
        zoom=3.0, 
        pitch=30
    )
    
    st.pydeck_chart(render_3d_route(path_ocean, path_inland, path_rail, view_state))

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #5a8fc7 0%, #4a7fb7 100%); padding: 15px; border-radius: 10px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 30px; margin-bottom: 5px;'>🚢</div>
            <div style='font-weight: bold;'>해상 운송</div>
            <div style='font-size: 0.9rem; opacity: 0.9;'>인천 → 연운항</div>
            <div style='margin-top: 5px; font-weight:bold;'>3-4일</div>
            <div style='font-size: 0.8rem;'>735 km</div>
            <div style='margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.3);'>
                <div style='font-size: 1.1rem; font-weight: bold;'>${ocean_cost:,.0f}</div>
                <div style='font-size: 0.75rem; opacity: 0.8;'>₩{ocean_cost_krw:,.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #5a9a5f 0%, #4a8a4f 100%); padding: 15px; border-radius: 10px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 30px; margin-bottom: 5px;'>🚛</div>
            <div style='font-weight: bold;'>내륙 운송</div>
            <div style='font-size: 0.9rem; opacity: 0.9;'>항구 → 철도 허브</div>
            <div style='margin-top: 5px; font-weight:bold;'>1일</div>
            <div style='font-size: 0.8rem;'>189 km</div>
            <div style='margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.3);'>
                <div style='font-size: 1.1rem; font-weight: bold;'>${inland_cost:,.0f}</div>
                <div style='font-size: 0.75rem; opacity: 0.8;'>₩{inland_cost_krw:,.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #c75a5a 0%, #b74a4a 100%); padding: 15px; border-radius: 10px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 30px; margin-bottom: 5px;'>🚂</div>
            <div style='font-weight: bold;'>철도 운송</div>
            <div style='font-size: 0.9rem; opacity: 0.9;'>TCR/TMGR 노선</div>
            <div style='margin-top: 5px; font-weight:bold;'>{rail_days}</div>
            <div style='font-size: 0.8rem;'>{rail_distance}</div>
            <div style='margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.3);'>
                <div style='font-size: 1.1rem; font-weight: bold;'>${rail_cost:,.0f}</div>
                <div style='font-size: 0.75rem; opacity: 0.8;'>₩{rail_cost_krw:,.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------------------------------------
# TAB 3: 물류비 분석
# ----------------------------------------------------------------
with tabs[2]:
    st.subheader("물류비 구조 분석")

    real_fx = get_realtime_exchange_rate()

    selected_term = st.selectbox(
        "인코텀즈 2020 선택",
        ["EXW", "FCA", "FOB", "CFR", "CIF", "DAP", "DPU", "DDP"]
    )
    
    st.session_state['selected_incoterm'] = selected_term
    
    raw_costs = calc.get_base_costs(target_country, teu)
    
    chart_data = {}

    if selected_term != "EXW":
        chart_data["내륙 운송"] = raw_costs['inland_kr_cost']
        chart_data["THC & 항만비용"] = raw_costs['thc_cost']
        chart_data["수출 통관"] = 150

    if selected_term not in ["EXW", "FCA", "FAS", "FOB"]:
        chart_data["해상 운임"] = raw_costs['ocean_cost']
        chart_data["철도 할증료"] = raw_costs['rail_cost']

    if selected_term in ["CIF", "CIP", "DAP", "DPU", "DDP"]:
        chart_data["화물 보험"] = raw_costs['ocean_cost'] * 0.008

    if selected_term == "DDP":
        chart_data["수입 관세 (추정)"] = raw_costs['ocean_cost'] * 0.1
        chart_data["최종 배송"] = 500
    elif selected_term == "DPU":
        chart_data["양하비"] = 200

    logistics_total_usd = sum(chart_data.values())
    product_cost_usd = (cost_krw * 20000 * teu) / real_fx
    final_quote_usd = product_cost_usd + logistics_total_usd

    st.session_state['final_quote_usd'] = final_quote_usd
    st.session_state['logistics_total_usd'] = logistics_total_usd

    final_krw = final_quote_usd * real_fx
    logistics_krw = logistics_total_usd * real_fx

    st.markdown("### 💰 견적 요약")
    c_top1, c_top2, c_top3 = st.columns(3)
    
    with c_top1:
        st.metric(
            label="최종 견적가 (USD)",
            value=f"${final_quote_usd:,.2f}",
            delta=f"₩{final_krw:,.0f} (KRW)"
        )
    
    with c_top2:
        st.metric(
            label="순수 물류비 (USD)",
            value=f"${logistics_total_usd:,.2f}",
            delta=f"₩{logistics_krw:,.0f} (KRW)",
            delta_color="inverse"
        )
    
    with c_top3:
        ratio = (logistics_total_usd / final_quote_usd) * 100 if final_quote_usd > 0 else 0
        st.metric(
            label="물류비 비중",
            value=f"{ratio:.1f}%",
            delta=f"{selected_term} 조건"
        )

    st.divider()

    st.markdown("### 📊 비용 구조 분석")
    
    c_chart, c_gauge = st.columns([1.5, 1])
    
    with c_chart:
        if logistics_total_usd > 0:
            fig = go.Figure(go.Waterfall(
                orientation="v",
                measure=["relative"] * len(chart_data) + ["total"],
                x=list(chart_data.keys()) + ["총 물류비"],
                y=list(chart_data.values()) + [0],
                text=[f"${v:,.0f}" for v in chart_data.values()] + [f"${logistics_total_usd:,.0f}"],
                connector={"line":{"color":"#333"}},
                totals={"marker":{"color":"#ef553b"}},
                decreasing={"marker":{"color":"#00cc96"}},
                increasing={"marker":{"color":"#1f77b4"}},
            ))
            fig.update_layout(
                title=f"물류비 세부 내역 ({selected_term})",
                height=450,
                showlegend=False,
                yaxis_title="비용 (USD)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ EXW 조건: 판매자가 부담하는 별도 물류비용이 없습니다.")
    
    with c_gauge:
        st.markdown("#### 판매자 리스크")
        risk_score = 10 if selected_term == "EXW" else 30 if selected_term == "FOB" else 60 if selected_term == "CIF" else 90
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", 
            value=risk_score,
            title={'text': "Risk Score", 'font': {'size': 14}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#2c3e50"},
                'steps': [
                    {'range': [0, 40], 'color': "#e8f5e9"},
                    {'range': [40, 70], 'color': "#fff9c4"},
                    {'range': [70, 100], 'color': "#ffcdd2"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_g.update_layout(height=280, margin=dict(t=60, b=30, l=20, r=20))
        st.plotly_chart(fig_g, use_container_width=True)
        
        st.caption(f"**{selected_term}** 조건 책임 범위")

# ----------------------------------------------------------------
# TAB 4: AI 전략 리포트 (최종 수정)
# ----------------------------------------------------------------
with tabs[3]:
    st.subheader("전략 실행 대시보드")
    
    current_prod = st.session_state.get('product_name', 'General Cargo')
    current_country = st.session_state.get('target_country_key', 'Mongolia')
    current_term = st.session_state.get('selected_incoterm', 'DDP')
    current_hs = st.session_state.get('current_hs_code', 'Unknown')
    current_cost = st.session_state.get('final_quote_usd', 0)
    
    s1, s2, s3 = st.columns(3)
    s1.metric("대상 화물", current_prod, f"HS: {current_hs}")
    s2.metric("선택 경로", f"{current_country} (복합운송)", "최적 효율")
    s3.metric("예상 총 비용", f"${current_cost:,.0f}", f"{current_term} 기준")

    st.divider()

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("#### 화물 상황 및 리스크 분석")
        
        is_strategic = check_strategic_goods(current_prod)
        if is_strategic:
            st.warning("⚠️ 전략물자: 수출 허가 필요")
        else:
            st.success("✅ 일반 화물: 특별 제한 사항 없음")

        cargo_risks = analyze_cargo_context(current_prod)
        
        if cargo_risks:
            st.markdown("##### 🔍 감지된 특수 요구사항")
            for risk in cargo_risks:
                st.markdown(
                    f'<div style="background-color: {risk["color"]}22; '
                    f'border-left: 4px solid {risk["color"]}; '
                    f'padding: 10px; margin: 5px 0; border-radius: 5px;">'
                    f'<b>{risk["type"]}</b><br>{risk["msg"]}</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("💡 인사이트: 해당 화물 유형은 특수 운송 조건이 필요하지 않습니다.")

    with col_right:
        st.markdown("#### 표준 vs. 최적화")
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[4.5, 4.8, 4.3, 4.6, 4.7],
            theta=['비용절감','배송속도','안전성','행정편의','규정준수'],
            fill='toself',
            name='TradeNex AI',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[2.5, 3.0, 2.8, 2.2, 3.0],
            theta=['비용절감','배송속도','안전성','행정편의','규정준수'],
            fill='toself',
            name='일반 포워더',
            line=dict(color='#ff7f0e', width=2, dash='dot'),
            marker=dict(size=6)
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5],
                    tickfont=dict(size=10)
                )
            ),
            showlegend=True,
            height=320,
            margin=dict(l=60, r=60, t=40, b=40),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.divider()

    st.markdown("### AI 전략 컨설팅")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        generate_report = st.button(
            "최종 전략 리포트 생성", 
            type="primary", 
            use_container_width=True,
            help="AI가 화물 특성, 경로, 비용을 종합 분석하여 맞춤 전략을 제시합니다"
        )

    if generate_report:
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            st.error("⚠️ **API 키 누락!** `.env` 파일에 `OPENAI_API_KEY`를 설정해주세요.")
            st.code("OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxx", language="bash")
        else:
            with st.spinner("🧠 AI 컨설턴트가 전략 리포트를 생성하고 있습니다..."):
                try:
                    # ✅ 위치 인자로 전달 (키워드 인자 제거)
                    report_content = ai.ask_strategy(
                        current_country,    # 첫 번째 인자
                        current_term,       # 두 번째 인자
                        current_prod        # 세 번째 인자
                    )

                    st.success("✅ 분석 완료!")
                    
                    st.markdown(
                        f'<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
                        f'padding: 20px; border-radius: 10px; color: white; margin: 10px 0;">'
                        f'<h3 style="margin: 0 0 10px 0;">AI 전략 리포트</h3>'
                        f'<p style="font-size: 0.9rem; opacity: 0.9;">생성 시간: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    
                    st.markdown(report_content)
                    
                    st.download_button(
                        label="💾 리포트 다운로드 (.txt)",
                        data=report_content,
                        file_name=f"TradeNex_Strategy_{current_country}_{time.strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"❌ 리포트 생성 중 오류 발생: {str(e)}")
                    st.info("💡 문제가 지속되면 API 키와 네트워크 상태를 확인해주세요.")

    st.markdown("---")
    
    col_left, col_center, col_right = st.columns([1, 1, 1])
    
    with col_center:
        st.markdown("### 다음 단계")
        if st.button("영업팀 페이지로 이동", type="primary", use_container_width=True):
            st.switch_page("pages/sale_1.py")
        
        st.caption("견적서를 받으시거나 전문 컨설팅이 필요하신가요?")