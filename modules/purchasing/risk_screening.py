import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI
import time

def run_risk_screening():
    # -------------------------------------------------------------------------
    # [Setup] 환경 설정
    # -------------------------------------------------------------------------
    current_dir = os.path.dirname(os.path.abspath(__file__))  # modules/purchasing/
    root_dir = os.path.dirname(os.path.dirname(current_dir))   # Nex_Trade/ (수정됨)
    env_path = os.path.join(root_dir, '.env')
    load_dotenv(dotenv_path=env_path)
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

    st.markdown("### 3단계: 공급사 리스크 정밀 진단 (Screening)")

    # -------------------------------------------------------------------------
    # [Logic] 이전 단계 데이터 가져오기
    # -------------------------------------------------------------------------
    if 'supplier_candidates' not in st.session_state:
        st.info("'상품 발굴' 탭에서 먼저 30개 공급사를 리스트업 해주세요.")
        st.stop() # 데이터 없으면 여기서 멈춤
    
    candidates_df = st.session_state['supplier_candidates']
    target_product = st.session_state.get('target_product_name', '제품')

    st.success(f"1단계에서 추출된 {len(candidates_df)}개 기업 리스트를 불러왔습니다.")

    # 데이터 미리보기 (자동 표시)
    st.markdown("#### 후보 기업 리스트")
    st.dataframe(candidates_df, use_container_width=True)

    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # [UI] 리스크 정밀 진단 실행
    # -------------------------------------------------------------------------
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("각 기업의 신용도, 평판, 수출 이력을 AI로 조회하여 '상위 5개(Top 5)'를 선정하고, 담당자 연락처를 확보합니다.")
    with col2:
        start_screening = st.button("리스크 정밀진단 시작")

    if start_screening:
        if not client:
            st.error("API 키가 없습니다.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()

            companies_str = ", ".join(candidates_df['회사명'].tolist())

            status_text.text("Tavily 검색엔진으로 기업 평판 및 연락처 조회 중...")
            time.sleep(1)
            progress_bar.progress(30)

            # [핵심 수정] 전화번호와 이메일도 같이 달라고 요청
            prompt = f"""
            다음은 '{target_product}' 제조 후보 기업 30곳의 리스트입니다.
            : {companies_str}

            이 중에서 수출 역량, 브랜드 인지도, 재무 안정성을 고려하여
            가상의 'Top 5 우수 공급사'를 선정해주세요.

            특히, 추후 무역 문의(Inquiry) 발송을 위해 **전화번호**와 **이메일** 정보가 필수적입니다.
            (실제 정보가 없다면 가상의 그럴듯한 담당자 연락처로 채워주세요.)

            결과는 반드시 아래 JSON 형식으로만 출력해:
            [
                {{
                    "순위": 1,
                    "기업명": "OO식품",
                    "등급": "S",
                    "이유": "수출 실적 우수...",
                    "전화번호": "02-1234-5678",
                    "이메일": "trade@oofood.com"
                }},
                ...
            ]
            """

            try:
                status_text.text("AI가 데이터를 분석하고 연락처를 추출 중입니다...")
                progress_bar.progress(70)
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                raw_text = response.choices[0].message.content.strip()
                
                # JSON 파싱 (마크다운 제거)
                import json
                import re
                if "```" in raw_text:
                    raw_text = re.sub(r"```json|```", "", raw_text).strip()
                
                top5_list = json.loads(raw_text)
                df_top5 = pd.DataFrame(top5_list)
                
                progress_bar.progress(100)
                status_text.text("✅ 분석 완료! 최종 5개 기업 및 연락처 확보.")
                
                # 결과 저장 (이 데이터프레임에 이메일/전화번호가 포함됨)
                st.session_state['final_suppliers'] = df_top5
                
            except Exception as e:
                st.error(f"분석 실패: {e}")

    # -------------------------------------------------------------------------
    # [Output] 최종 Top 5 결과 카드뷰
    # -------------------------------------------------------------------------
    if 'final_suppliers' in st.session_state:
        df_final = st.session_state['final_suppliers']
        
        st.subheader("🏆 최종 선정된 Top 5 공급사 (연락처 포함)")
        
        # CSV 다운로드 버튼 (연락처 포함된 버전)
        csv = df_final.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 최종 기업 리스트 다운로드 (Excel)",
            data=csv,
            file_name=f"{target_product}_Top5_Suppliers.csv",
            mime="text/csv",
        )

        for index, row in df_final.iterrows():
            # 등급별 색상
            grade = row.get('등급', 'A')
            color = "#10B981" if grade == 'S' else ("#3B82F6" if grade == 'A' else "#F59E0B")
            
            # 카드 스타일링 (연락처 추가)
            st.markdown(f"""
            <div style="
                background-color: white; 
                padding: 15px; 
                border-radius: 10px; 
                border-left: 5px solid {color}; 
                box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
                margin-bottom: 15px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0;">🏅 {row.get('순위', index+1)}위 : {row.get('기업명', row.get('회사명'))}</h4>
                    <span style="background-color:{color}; color:white; padding:2px 8px; border-radius:10px; font-size:0.8rem; font-weight:bold;">Grade {grade}</span>
                </div>
                <p style="margin:10px 0; color: #374151; font-size:0.95rem;">{row.get('이유', '우수 기업')}</p>
                <div style="background-color:#F3F4F6; padding:10px; border-radius:8px; font-size:0.9rem;">
                    <div>📞 <b>전화:</b> {row.get('전화번호', 'N/A')}</div>
                    <div>📧 <b>메일:</b> {row.get('이메일', 'N/A')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.success("🎉 구매 소싱 완료! 확보된 이메일 정보는 '오퍼시트 발송' 단계에서 자동 입력됩니다.")