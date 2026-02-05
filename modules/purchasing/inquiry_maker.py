import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# =========================================================================
# [Setup] 환경 설정
# =========================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
env_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# [수정 1] 함수 인자에 'extra_options' 추가 (기본값 빈 리스트)
def generate_draft(supplier_name, my_info, item_info, extra_options=[]):
    """OpenAI를 이용해 비즈니스 메일 초안 생성"""
    if not client: 
        return "⚠️ 오류: .env 파일에서 API 키를 찾을 수 없습니다."
    
    # [수정 2] 추가 옵션이 있을 경우 프롬프트에 넣을 텍스트 생성
    extra_req_text = ""
    if extra_options:
        extra_req_text = "\n    [추가 선택 요청 사항]\n" + "\n".join([f"    - {opt}" for opt in extra_options])

    prompt = f"""
    당신은 무역 상사의 전문 바이어입니다. 아래 정보를 바탕으로 정중한 '국문 견적 의뢰 이메일(Inquiry)'을 작성하세요.
    
    [수신자] {supplier_name} 담당자님
    [발신자] {my_info['company']} {my_info['name']}
    [의뢰 품목] {item_info}
    
    [필수 요청 사항]
    1. MOQ (최소 주문 수량) 및 수량별 단가표 (Price List)
    2. 제품 상세 사양서 (Spec Sheet) 및 시험 성적서
    3. 납기(Lead Time) 및 결제 조건
    {extra_req_text}
    
    [톤앤매너]
    - 정중하고 격식 있는 비즈니스 한국어 사용.
    - 제목과 본문을 명확히 구분할 것.
    - 추가 선택 요청 사항이 있다면 본문에 자연스럽게 녹여낼 것.
    """
    
    try:
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role":"user", "content":prompt}],
            temperature=0.7
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"작성 중 오류 발생: {e}"

# =========================================================================
# [Main Function] 외부 호출용
# =========================================================================
def run_inquiry_maker():

    st.markdown("### 4단계: 견적 의뢰서 (Inquiry) 작성")
    st.info("선정된 Top 5 공급사에게 보낼 메일 초안을 AI가 대신 작성해줍니다.")

    if 'final_suppliers' not in st.session_state:
        st.error("2단계(리스크 평가) 결과가 없습니다. 이전 단계를 먼저 완료해주세요.")
        return

    df_suppliers = st.session_state['final_suppliers']
    default_item = st.session_state.get('target_product_name', '')

    # [수정 3] 사용자 입력 UI에 체크박스 로직 통합
    with st.expander("발신자 정보 및 옵션 설정", expanded=True):
        st.markdown("###### 1. 기본 정보")
        c1, c2 = st.columns(2)
        my_company = c1.text_input("나의 회사명", "넥스트레이드(주)")
        my_name = c2.text_input("담당자명", "김무역 팀장")
        detail_item = st.text_input("구체적 품목명", value=default_item)
        
        st.markdown("---")
        st.markdown("###### 2. 추가 문의 사항 (선택)")
        # 요청하신 체크박스 코드 삽입
        co1, co2, co3 = st.columns(3)
        opt1 = co1.checkbox("견본 요구 (Sample)")
        opt2 = co1.checkbox("결제 조건 (Payment)")
        opt3 = co2.checkbox("인증 서류 (Certi)")
        opt4 = co2.checkbox("OEM/ODM 가능 여부")
        opt5 = co3.checkbox("포장 사양 (Packing)")
        opt6 = co3.checkbox("카탈로그 (Catalog)")

        # 선택된 옵션을 리스트로 변환
        selected_options = []
        if opt1: selected_options.append("견본(샘플) 제공 가능 여부 및 절차 확인")
        if opt2: selected_options.append("대금 결제 조건(T/T, L/C 등) 및 시기 협의")
        if opt3: selected_options.append("품질 인증서(HACCP, ISO, 수출 허가서 등) 사본 요청")
        if opt4: selected_options.append("PB 상품 제작 또는 OEM/ODM 생산 대응 가능 여부 확인")
        if opt5: selected_options.append("물류 적재용 팔레트 규격 및 CBM 정보 요청")
        if opt6: selected_options.append("취급 품목 전체 카탈로그 및 브로슈어 요청")

    st.markdown("---")

    # 3. 공급사 리스트 출력 및 생성 버튼
    for idx, row in df_suppliers.iterrows():
        comp_name = row.get('기업명', '업체명 미상')
        email = row.get('이메일', '정보 없음')

        with st.container():
            c1, c2 = st.columns([3, 1])

            with c1:
                st.write(f"**{comp_name}** ({email})")
                draft_area = st.empty() # 결과가 들어갈 파란색 네모 위치

            with c2:
                if st.button(f"초안 생성", key=f"btn_{idx}"):
                    if not client:
                         st.error("API 키 오류")
                    else:
                        with st.spinner("AI가 비즈니스 메일을 작성 중입니다..."):
                            my_info = {"company": my_company, "name": my_name}

                            # [수정 4] generate_draft 함수에 selected_options 리스트 전달
                            draft = generate_draft(comp_name, my_info, detail_item, selected_options)

                            with draft_area.container():
                                st.success(f"To: {comp_name}")
                                st.text_area(f"메일 내용 ({comp_name})", value=draft, height=300)
            st.divider()

