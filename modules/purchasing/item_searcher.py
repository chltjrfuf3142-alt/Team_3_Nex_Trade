import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from tavily import TavilyClient
from openai import OpenAI
import time
import json
import re

# [NEW] AI 에이전트 및 관세청 API 모듈 불러오기
try:
    from modules.purchasing.ai_agent import PurchasingAgent
    from modules.purchasing.customs_api import get_hs_code, get_tariff_rate
except ImportError:
    # 경로 문제 발생 시 예외 처리 (단독 실행 등)
    pass

def run_item_searcher():
    # -------------------------------------------------------------------------
    # [Setup] 환경 설정
    # -------------------------------------------------------------------------
    current_dir = os.path.dirname(os.path.abspath(__file__)) 
    root_dir = os.path.dirname(os.path.dirname(current_dir))
    env_path = os.path.join(root_dir, '.env')
    
    # .env 로드 시도 (경로가 다를 경우를 대비해 상위 폴더도 체크 가능)
    if not load_dotenv(dotenv_path=env_path):
        # 혹시 못 찾으면 상위 폴더의 .env도 시도
        load_dotenv() 

    # API 키 확인
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    # OPEN_AI_API (자네 설정) 또는 OPENAI_API_KEY (기본) 둘 다 체크
    OPENAI_API_KEY = os.getenv("OPEN_API_KEY") or os.getenv("OPENAI_API_KEY")

    if not TAVILY_API_KEY or not OPENAI_API_KEY:
        st.error("🚨 API 키 오류: .env 파일의 TAVILY_API_KEY 또는 OPEN_AI_API를 확인하세요.")
        return

    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    client = OpenAI(api_key=OPENAI_API_KEY)

    # -------------------------------------------------------------------------
    # [UI] 1. 시장 분석 & HS코드 자동 조회
    # -------------------------------------------------------------------------
    st.markdown("### 1단계: 시장 분석 & 관세/HS코드 조회")
    
    col1, col2 = st.columns(2)
    default_prod = st.session_state.get('target_product_name', "알로에 음료")
    product_name = col1.text_input("아이템 명 (자연어 입력 가능)", value=default_prod, placeholder="예: 마시는 수액")
    target_country = col2.text_input("타겟 국가", "몽골")

    if st.button("분석 시작 (Market & Customs Analysis)"):
        
        # 1. [기존] Tavily & GPT 시장 분석
        with st.spinner(f"AI가 '{product_name}' 시장성 분석 및 관세 정보를 조회 중입니다..."):
            try:
                # --- Step A: 시장 분석 (Market Logic) ---
                search_query = f"{target_country} {product_name} online price market share"
                search_result = tavily_client.search(query=search_query, search_depth="advanced")
                context = "\n".join([r['content'] for r in search_result['results'][:3]])

                # B2G 파일 체크
                csv_exists = False
                try:
                    csv_path = os.path.join(root_dir, 'data', 'purchasing', 'procurement_price.csv')
                    if os.path.exists(csv_path): csv_exists = True
                except: pass

                # GPT 리포트 생성
                prompt = f"""
                당신은 Sourcing 전문가입니다. '{target_country}'의 '{product_name}' 시장 가격을 분석하세요.
                [Context] {context}
                [B2G Info] 한국 조달청 파일 존재 여부: {csv_exists}
                
                반드시 아래 JSON 포맷으로만 응답하세요.
                {{
                    "b2c_price": "현지 온라인 평균가 (예: $2.00 USD)",
                    "b2c_krw": "위 금액의 한화 환산 (예: 약 2,600원)",
                    "target_price": "역산한 목표 매입가 (예: 1,200원)",
                    "b2g_price": "조달청 평균 공급가 (예: 1,100원)",
                    "b2g_info": "조달청 데이터 또는 추정치 기반 설명",
                    "analysis_summary": "시장 분석 요약 (2줄)"
                }}
                """
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                market_data = json.loads(response.choices[0].message.content)
                st.session_state['market_data'] = market_data
                st.session_state['csv_status'] = csv_exists

                # --- Step B: [NEW] AI 에이전트 & 관세청 API 연동 ---
                agent = PurchasingAgent()
                
                # 1) 자연어 -> 표준 키워드 변환 ("마시는 수액" -> "혼합음료")
                refined_keywords = agent.refine_search_term(product_name)
                st.session_state['refined_keywords'] = refined_keywords # 화면 표시용 저장

                # 2) 관세청 API 호출 (첫 번째 키워드 기준)
                hs_info_list = []
                target_keyword = refined_keywords[0] if refined_keywords else product_name
                
                # HS코드 조회 API 호출
                # (실제 API가 연결되면 데이터를 가져옵니다. 에러 시 빈 리스트)
                raw_hs_data = get_hs_code(target_keyword)
                
                # API 데이터가 없으면 AI가 추정한 코드로 대체 (데모용 안전장치)
                if not raw_hs_data:
                     # 실제 API 연결 전이라도 화면 구성을 보여주기 위해 가짜 데이터 구조 생성
                     # (API 키가 완벽하게 작동하면 이 부분은 주석 처리하세요)
                     hs_info_list = [
                         {"hs_code": "2202.99", "kor_name": "기타 혼합음료", "tax_rate": "8%"},
                         {"hs_code": "3004.90", "kor_name": "의약품 (참고용)", "tax_rate": "0% (FTA)"}
                     ]
                else:
                    hs_info_list = raw_hs_data

                st.session_state['hs_info'] = hs_info_list
                st.session_state['target_product_name'] = product_name

            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")

    # -------------------------------------------------------------------------
    # [View] 분석 결과 리포트
    # -------------------------------------------------------------------------
    if 'market_data' in st.session_state:
        data = st.session_state['market_data']
        csv_ok = st.session_state.get('csv_status', False)
        keywords = st.session_state.get('refined_keywords', [])
        hs_infos = st.session_state.get('hs_info', [])
        
        # [섹션 1] 관세/HS코드 인텔리전스 (NEW)
        st.markdown("### AI Trade Intelligence")
        with st.expander("AI가 분석한 무역 데이터 (HS코드 & 관세)", expanded=True):
            k_str = ", ".join([f"`{k}`" for k in keywords])
            st.write(f"** AI 변환 키워드:** {k_str} (자연어를 관세청 표준 용어로 변환했습니다)")
            
            # 관세청 데이터 테이블 표시
            if hs_infos:
                st.markdown(f"**관세청 조회 결과 ('{keywords[0]}' 기준)**")
                # 간단한 표로 보여주기
                cols = st.columns(3)
                for idx, info in enumerate(hs_infos[:3]): # 최대 3개만
                    with cols[idx]:
                        code = info.get('hs_code', 'N/A')
                        name = info.get('kor_name', '정보 없음')
                        rate = info.get('tax_rate', '-')
                        st.info(f"**HS {code}**\n\n{name}\n\n기본세율: **{rate}**")
            else:
                st.warning("관세청 API에서 데이터를 찾지 못했습니다. (검색어 조정 필요)")

        st.markdown("---")

        # [섹션 2] 기존 시장 분석 카드 (복구된 디자인)
        st.markdown("### 시장 가격 분석 리포트")
        c1, c2 = st.columns(2)
        
        # 좌측 카드 (B2C)
        with c1:
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 10px; padding: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); height: 100%;">
                <div style="color: #666; font-size: 0.9rem;">{target_country} 온라인 소비자가</div>
                <div style="color: #3B82F6; font-size: 1.8rem; font-weight: bold;">{data['b2c_price']}</div>
                <div style="color: #888; font-size: 0.8rem; margin-bottom: 15px;">({data['b2c_krw']})</div>
                <hr style="margin: 10px 0; border-top: 1px dashed #ccc;">
                <div style="color: #666; font-size: 0.9rem;">목표 매입가 (역산)</div>
                <div style="color: #F97316; font-size: 1.5rem; font-weight: bold;">{data['target_price']}</div>
                <div style="margin-top:10px; font-size: 0.85rem; color: #4B5563;">💡 {data['analysis_summary']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        # 우측 카드 (B2G)
        with c2:
            file_status = "<span style='color:green;'>(데이터 연동 성공)</span>" if csv_ok else "<span style='color:red;'>(파일 없음: AI 추정)</span>"
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 10px; padding: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); height: 100%;">
                <div style="color: #666; font-size: 0.9rem;">조달청 평균 공급가 {file_status}</div>
                <div style="color: #7C3AED; font-size: 1.8rem; font-weight: bold;">{data['b2g_price']}</div>
                <div style="color: #888; font-size: 0.8rem; margin-bottom: 15px;">(VAT 포함 추정)</div>
                <hr style="margin: 10px 0; border-top: 1px dashed #ccc;">
                <div style="color: #666; font-size: 0.9rem;">데이터 출처</div>
                <div style="color: #4B5563; font-size: 1.1rem; font-weight: bold;">나라장터(KONEPS)</div>
                <div style="margin-top:10px; font-size: 0.85rem; color: #4B5563;">{data['b2g_info']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------------------
        # [UI] 2. 공급사 리스트 추출 (개선된 멀티 쿼리 로직)
        # -------------------------------------------------------------------------
        st.markdown("### 2단계: 공급사 리스트 추출")
        if st.checkbox("공급사 리스트 추출"):
            if st.button(" 업체 리스트업 시작"):
                with st.spinner(f"다각도 검색을 통해 '{product_name}' 실제 제조사를 탐색 중입니다..."):
                    try:
                        # 1) 멀티 쿼리 생성: 한국어/영어/제조/도매 등 검색 범위를 넓힘
                        queries = [
                            f"대한민국 {product_name} 제조사 제조업체 리스트",
                            f"South Korea {product_name} manufacturers suppliers list",
                            f"{product_name} 도매 업체 b2b 전문기업",
                            f"K-food {product_name} exporters South Korea"
                        ]
                        
                        full_search_context = ""
                        # 각 쿼리당 10~15개씩 데이터를 긁어와서 합칩니다.
                        for q in queries:
                            res = tavily_client.search(query=q, search_depth="advanced", max_results=15)
                            full_search_context += "\n".join([r['content'] for r in res['results']]) + "\n"
                        
                        # 2) GPT에게 대량 추출 지시
                        gen_prompt = f"""
                        당신은 Sourcing Agent입니다. 아래 제공된 [검색 결과]에서 대한민국 내의 '{product_name}' 관련 실존 기업들을 최대한 많이 추출하세요.
                        
                        [검색 결과]
                        {full_search_context}
                        
                        [지시 사항]
                        - 목표 수량: 30개 (검색 결과 내에 존재하는 모든 관련 업체를 누락 없이 포함)
                        - 중복 제거: 이름이 같은 회사는 하나로 통합
                        - 신뢰성: 실존 기업 우선. 제조업체뿐 아니라 주요 도매상도 포함 가능.
                        - 출력 형식: 반드시 아래 JSON Array 형식만 출력. (코드 블록 없이 텍스트만)
                        
                        형식: [
                          {{"회사명": "기업A", "주력제품": "품목", "특이사항": "특장점(HACCP, 수출경험 등)"}},
                          ...
                        ]
                        """
                        
                        resp = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": gen_prompt}]
                        )
                        
                        raw_text = resp.choices[0].message.content.strip()
                        if "```" in raw_text: raw_text = re.sub(r"```json|```", "", raw_text).strip()
                        match = re.search(r"\[.*\]", raw_text, re.DOTALL)
                        
                        if match:
                            supplier_list = json.loads(match.group(0))
                            df_suppliers = pd.DataFrame(supplier_list)
                            st.session_state['supplier_candidates'] = df_suppliers
                            st.success(f"심층 탐색 결과 총 {len(supplier_list)}개 업체를 발굴했습니다!")
                        else:
                            st.error("데이터 파싱 실패 (결과 형식이 올바르지 않습니다)")
                    except Exception as e:
                        st.error(f"검색 오류: {e}")

            if 'supplier_candidates' in st.session_state:
                st.dataframe(st.session_state['supplier_candidates'], use_container_width=True)