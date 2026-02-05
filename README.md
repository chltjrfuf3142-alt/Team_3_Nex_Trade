# 🌏 TradeNex: AI 기반 글로벌 무역 통합 플랫폼

**TradeNex**는 무역 상사의 업무 효율화를 위해 **구매(Purchasing), 물류(Logistics), 영업(Sales)**의 전 과정을 하나의 대시보드에서 통합 관리하는 AI 기반 플랫폼입니다.

---

## 📌 프로젝트 소개 (Project Overview)

본 프로젝트는 기존의 파편화된 무역 업무를 **Streamlit**을 활용하여 웹 애플리케이션으로 통합하였습니다.
OpenAI(GPT-4o)와 Tavily(Search) API를 활용하여 **시장 분석, 공급사 리스크 평가, 물류비 최적화, 오퍼시트 작성**을 자동화합니다.

### 🎯 핵심 목표
- **Sourcing:** AI 검색을 통한 유망 아이템 발굴 및 최적 공급사 매칭
- **Logistics:** 실제 운임 데이터(HMM, LX 등) 기반의 정교한 물류비 산출
- **Sales:** 마진율 시뮬레이션 및 바이어 맞춤형 오퍼시트 자동 생성

---

## 🚀 주요 기능 (Key Features)

### 🏠 Control Tower (통합 대시보드)
- **실시간 KPI 모니터링**: 프로젝트 진행 단계 및 핵심 지표 시각화
- **3단계 워크플로우**: Purchasing → Logistics → Sales 통합 프로세스
- **로그인 시스템**: 사용자 인증 (기본 계정: 박도영/1234)

### 🛒 Purchasing (구매 모듈)

#### 1. Item Searcher (시장 분석)
- **Tavily API 기반 시장 조사**: 실시간 온라인 가격 정보 수집
- **B2C 가격 분석**: 소비자 시장 가격 역산
- **목표 수입 가격 계산**: 역계산을 통한 적정 매입가 산출
- **B2G(조달청) 데이터 매칭**: 정부 조달 가격 참조
- **공급사 후보 생성**: 30개 국내 제조사 자동 추천
- **CSV 내보내기**: 분석 결과 다운로드

#### 2. Risk Screening (리스크 평가)
- **AI 기반 신용도 평가**: GPT를 활용한 공급사 신뢰성 분석
- **등급 산정**: S/A/B 등급 자동 부여
- **연락처 추출**: 이메일, 전화번호 자동 수집
- **Top 5 추천**: 최적 공급사 랭킹

#### 3. Inquiry Maker (RFQ 생성)
- **자동 견적 요청서 작성**: 표준화된 RFQ 문서 생성

---

### 🚢 Logistics (물류 모듈)

#### 1. Cost Calculator (비용 계산)
- **실제 운임 데이터 활용**: HMM, LX Pantos, Glovis 데이터 기반
- **할증료 자동 계산**:
  - BAF (유류할증료): 10%
  - CAF (통화할증료): 5%
  - PSS (성수기할증료): 15%
- **복합 운송 견적**: 해상 + 철도 + 내륙 운송
- **계산 공식**: `ocean_cost = (base_rate × 1.10 × 1.05 × 1.15) × TEU`

#### 2. Incoterms Manager (인코텀즈)
- **13가지 조건 지원**: EXW, FOB, CFR, CIF, DAP, DDP 등
- **비용 분담 명확화**: 구매자/판매자 책임 범위 계산
- **조건별 원가 분해**: 단계별 비용 항목화

#### 3. Customs Broker (통관)
- **AI 기반 HS Code 조회**: 6자리 품목분류번호 자동 검색
- **관세율 추정**: 국가별 예상 관세율 제공
- **JSON 응답 파싱**: 구조화된 데이터 처리

#### 4. AI Consulting Agent
- **물류 전략 컨설팅**: GPT 기반 최적 전략 제안
- **필수 서류 체크리스트**: 통관/운송 필요 문서 안내
- **경로별 리스크 분석**: 위험 요소 사전 식별
- **전문적 어조**: 비즈니스 전문가 수준 응답

#### 5. Finance Module (금융)
- **실시간 환율 조회**: Frankfurter API 연동
- **Fallback 기능**: API 오류 시 1,380 KRW/USD 기본값

#### 6. Risk Manager (리스크 관리)
- **전략 물자 탐지**: 드론, 반도체, 미사일 등 민감 품목 식별
- **화물 컨텍스트 분석**: 냉동식품, 의약품, 위험물 등
- **색상 코드 알림**: 위험도별 시각적 경고

#### 7. Visualizer (시각화)
- **3D 지도**: PyDeck 기반 경로 시각화
- **다중 레이어**: 해상(파란색), 철도(빨간색), 내륙(녹색)
- **Waterfall 차트**: Plotly를 활용한 비용 분해도
- **다크 테마 맵**: Dark Matter 베이스맵 + 툴팁

---

### 💼 Sales (영업 모듈)

#### 1. Pricing Calculator (가격 산정)
- **3가지 마진 전략**:
  - **GEN (General)**: 28% - 대량 유통 제품 (OTS 모델)
  - **FUN (Functional)**: 45% - 건강기능식품 (AMOREPACIFIC 참조)
  - **PRE (Premium)**: 96% - 럭셔리 제품 (Amorepacific 참조)
- **계산 공식**: `Price = Cost × (1 + margin_rate)`
- **비용 분해 차트**: 원가/마진 시각화 (Pie Chart)

#### 2. AI Offer Writer (제안서 작성)
- **전문 오퍼 이메일 생성**: GPT-4o 또는 Claude 3 Opus 활용
- **다국어 지원**: Deep-translator 통한 자동 번역
- **비즈니스 어조**: 설득력 있는 전문 문체
- **개인화**: 바이어 맞춤형 내용 생성

#### 3. Document Maker (문서 출력)
- **.docx 내보내기**: python-docx를 활용한 Word 문서 생성
- **전문 서식**: 회사 헤더 및 표준 레이아웃
- **조건 명시**: 가격, 결제 조건, 배송 조건

#### 4. Market Data (시장 정보)
- **실시간 지표**:
  - USD/KRW 환율 (yfinance)
  - WTI 유가 (원유 선물)
  - 삼성전자 주가
- **글로벌 뉴스**: NewsAPI를 통한 무역 뉴스 피드
- **환율 히스토리**: 1개월 캔들 차트

---

## 🛠️ 기술 스택 (Tech Stack)

### Frontend
- **Streamlit**: 웹 애플리케이션 프레임워크
- **Plotly**: 인터랙티브 차트 및 그래프
- **PyDeck**: 지리 공간 데이터 시각화 (3D 지도)
- **Custom CSS**: 그라디언트 카드, 애니메이션, 반응형 디자인

### Backend & APIs
- **OpenAI GPT-4o/GPT-4o-mini**: AI 추론 및 문서 생성
- **Tavily Search API**: 시장 조사 및 경쟁사 분석
- **Anthropic Claude** (선택): 대체 AI 모델
- **yfinance**: 실시간 금융 데이터 (환율, 주가, 상품)
- **NewsAPI**: 글로벌 무역 뉴스
- **Frankfurter API**: 환율 데이터

### Data Processing
- **Pandas**: CSV 데이터 처리 및 분석
- **python-docx**: Word 문서 생성
- **deep-translator**: 다국어 번역
- **OpenPyXL**: Excel 내보내기

### Environment & Security
- **python-dotenv**: 환경 변수 관리
- **.env 파일**: API 키 보안 저장

---

## 📂 폴더 구조 (Project Structure)

```
Nex_Trade/
├── home.py                          # 메인 진입점 & 컨트롤 타워
├── config.py                        # 설정 및 기본값
├── requirements.txt                 # Python 의존성
├── .env.example                     # 환경 변수 템플릿
├── .gitignore                       # Git 제외 파일 목록
├── README.md                        # 프로젝트 문서
│
├── data/                            # 데이터 저장소
│   ├── purchasing/                  # [구매팀 데이터]
│   │   ├── food_manufacturers_cleaned.csv   # 국내 식품 제조사 DB
│   │   └── procurement_price.csv            # 조달청 나라장터 납품 단가
│   │
│   ├── logistics/                   # [물류팀 데이터]
│   │   ├── hmm_shipping_data.csv    # HMM 해상 운임 (2025 3Q)
│   │   ├── lx_inland.csv            # LX Pantos 내륙 운송
│   │   ├── lx_rail.csv              # TCR (Trans-China Railway)
│   │   ├── glocis_handle_data.csv   # Glovis 하역/핸들링/보험
│   │   └── WPI_data.csv             # World Port Index
│   │
│   └── sales/                       # [영업팀 데이터]
│       ├── global_buyers.csv        # 글로벌 바이어 프로필
│       └── margin.csv               # 품목별 마진율 전략
│
├── modules/                         # 비즈니스 로직 (Backend)
│   ├── __init__.py
│   ├── ui.py                        # 글로벌 UI/UX 스타일링 & 사이드바
│   │
│   ├── purchasing/                  # [구매 인텔리전스]
│   │   ├── __init__.py
│   │   ├── item_searcher.py         # AI 시장 분석
│   │   ├── risk_screening.py        # 공급사 리스크 평가
│   │   ├── inquiry_maker.py         # RFQ 생성
│   │   ├── ai_agent.py              # 구매 AI 에이전트
│   │   └── customs_api.py           # 관세청 HS코드/관세율 API
│   │
│   ├── logistics/                   # [운송 & 경로 최적화]
│   │   ├── __init__.py
│   │   ├── calculator.py            # 비용 계산 엔진
│   │   ├── incoterms.py             # Incoterms 2020 로직
│   │   ├── customs.py               # HS Code & 관세 추정
│   │   ├── ai_agent.py              # AI 전략 컨설팅
│   │   ├── finance.py               # 환율 API
│   │   ├── risk_manager.py          # 화물 리스크 분석
│   │   └── visualizer.py            # 3D 지도 & 차트
│   │
│   └── sales/                       # [영업 수익 최적화]
│       ├── __init__.py
│       ├── pricing.py               # 마진 계산기
│       ├── ai_writer.py             # AI 오퍼 이메일 작성
│       ├── doc_maker.py             # Word 문서 내보내기
│       ├── market_data.py           # 실시간 시장 지표
│       ├── buyer_search.py          # 바이어 탐색
│       ├── translator.py            # 다국어 번역 (18개국)
│       ├── dashboard.py             # 영업 대시보드
│       ├── offer_manager.py         # 오퍼 폼 관리
│       └── tab_handlers.py          # 탭 UI 핸들러
│
└── pages/                           # 프론트엔드 뷰 (Streamlit Pages)
    ├── purchasing_1.py              # 구매 워크플로우
    ├── logistics_1.py               # 물류 최적화
    └── sale_1.py                    # 영업 & 오퍼 관리
```

---

## ⚙️ 설치 및 실행 (Installation & Setup)

### 1. 사전 요구사항
- Python 3.8 이상
- pip (Python 패키지 관리자)

### 2. 저장소 클론
```bash
git clone <repository-url>
cd Nex_Trade
```

### 3. 가상환경 생성 (권장)
```bash
# 가상환경 버전
3.12

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. 의존성 설치
```bash
pip install -r requirements.txt
```

### 5. 환경 변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 API 키를 입력합니다:

```bash
# .env 파일 생성
cp .env.example .env
```

**.env 파일 예시**:
```env
# 필수 API 키
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
TAVILY_API_KEY=tvly-xxxxxxxxxxxxx

# 선택 API 키
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
NEWS_API_KEY=xxxxxxxxxxxxx

# 기타 도메인별 API 키
# (customs, HS code 조회 등)
```

### 6. 애플리케이션 실행
```bash
streamlit run home.py
```

브라우저에서 `http://localhost:8501` 접속

### 7. 로그인
- **ID**: `박도영`
- **비밀번호**: `1234`

---

## 📊 데이터 파일 설명

### Sales Data ([data/sales/](data/sales/))
- **global_buyers.csv**:
  - 4+ 바이어 프로필 (Monos Group, Nomin United, Tavan Bogd, CU Mongolia)
  - 필드: ID, Country, Name, Business, Founded, Capital, Description, Email

- **margin.csv**:
  - 3가지 제품 전략
  - 필드: Category_Code, Category_Name, Target_Product, Benchmark_Company, Margin_Rate, Logic_Summary

### Logistics Data ([data/logistics/](data/logistics/))
- **hmm_shipping_data.csv**: HMM 해상 운임 (2025 3분기)
- **lx_inland.csv**: LX Pantos 내륙 운송 요금
- **lx_rail.csv**: TCR (Trans-China Railway) 요금
- **glocis_handle_data.csv**: Glovis 하역 수수료, 환율, 보험
- **WPI_data.csv**: World Port Index

### Purchasing Data ([data/purchasing/](data/purchasing/))
- **food_manufacturers_cleaned.csv**: 국내 식품 업체 데이터베이스
- **procurement_price.csv**: 정부 조달청 (KONEPS) 가격

---

## 🔐 보안 및 인증

### 로그인 시스템
- 하드코딩된 인증 정보 (박도영/1234)
- `st.session_state['logged_in']` 기반 세션 관리
- **주의**: 프로덕션 환경에서는 보안 강화 필요

### API 키 관리
- `.env` 파일에 저장 (Git에서 제외)
- `.env.example`에 예시 제공
- 지원 키:
  - `OPENAI_API_KEY` - 필수
  - `TAVILY_API_KEY` - 구매 모듈용
  - `ANTHROPIC_API_KEY` - 선택 (Claude)
  - `NEWS_API_KEY` - 시장 뉴스용

---

## 💡 사용 흐름 (User Flow)

```
1. 로그인 ([home.py](home.py))
   └─> 대시보드: 3단계 워크플로우 확인

2. Purchasing 클릭 ([pages/purchasing_1.py](pages/purchasing_1.py))
   ├─ Step 1: 시장 분석
   │   ├─ 입력: 제품명, 목표 국가
   │   ├─ 처리: Tavily 검색 + GPT 분석
   │   └─ 출력: B2C 가격, 목표 수입가, B2G 참조
   │
   ├─ Step 2: 공급사 리스팅
   │   ├─ GPT가 30개 국내 제조사 생성
   │   └─ CSV 다운로드 가능
   │
   └─ Step 3: 리스크 스크리닝
       ├─ AI가 상위 5개 공급사 평가
       └─ 출력: 랭킹 + 연락처

3. Logistics 클릭 ([pages/logistics_1.py](pages/logistics_1.py))
   ├─ Tab 1: 화물 사양 입력
   │   ├─ 제품명, 중량, 목적지
   │   ├─ 컴플라이언스 체크리스트
   │   └─ 전략 물자 검사
   │
   ├─ Tab 2: 경로 시각화
   │   ├─ 3D 지도: 인천 → 롄윈강 → 몽골/카자흐스탄
   │   ├─ 경로 레이어: 해상(파랑), 철도(빨강), 내륙(초록)
   │   └─ 인터랙티브 툴팁
   │
   ├─ Tab 3: 비용 견적
   │   ├─ 기본 비용 + 할증료
   │   ├─ Incoterms 분해
   │   ├─ 관세 계산
   │   └─ 총 비용 (KRW)
   │
   └─ Tab 4: AI 컨설팅
       ├─ 전략 추천
       ├─ 서류 요구사항
       └─ 리스크 완화 조언

4. Sales 클릭 ([pages/sale_1.py](pages/sale_1.py))
   ├─ Market Watch (실시간)
   │   ├─ USD/KRW 환율
   │   ├─ WTI 유가
   │   ├─ 삼성전자 주가
   │   └─ 글로벌 무역 뉴스 피드
   │
   ├─ Pricing Simulator
   │   ├─ 입력: 제품명, 원가(USD), 카테고리
   │   ├─ 출력: 최종 판매가, 마진율, 전략 설명
   │   └─ 시각화: 원가 분해 파이 차트
   │
   └─ Offer Generation
       ├─ AI 작성 이메일
       ├─ 다국어 번역
       └─ .docx 내보내기
```

---

## 🏗️ 아키텍처 패턴

### 1. 세션 상태 관리
- `st.session_state`를 통한 페이지 간 데이터 흐름
- 예시 데이터: `market_data`, `supplier_candidates`, `calc_result`

### 2. 모듈 기반 설계
- 관심사 분리: UI (pages) vs. 로직 (modules)
- 각 팀(구매, 물류, 영업)별 전용 모듈 폴더

### 3. AI 기반 자동화
- GPT-4o: 전략 컨설팅 & 문서 생성
- Tavily: 시장 조사
- Claude (선택): 오퍼 작성 다양성

### 4. Fallback & 에러 처리
- CSV 로딩 실패 → 하드코딩된 기본값
- API 오류 → 캐시/추정값
- 예: 환율 API 오류 시 1,380 KRW/USD 사용

### 5. 데이터 파이프라인
```
CSV → Pandas → AI 처리 → Streamlit UI → 내보내기 (CSV/DOCX/XLSX)
```

---

## 🔄 기술 통합 흐름

```
┌─────────────────────────────────────────────────────────┐
│         Frontend: Streamlit Web UI                      │
│  (3-step workflow: Purchasing → Logistics → Sales)      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌──────────┐
   │ OpenAI  │  │ Tavily  │  │ yfinance │
   │ (GPT)   │  │(Search) │  │ (Markets)│
   └─────────┘  └─────────┘  └──────────┘
        │            │            │
        └────────────┼────────────┘
                     ▼
          ┌──────────────────────┐
          │ Local CSV Database   │
          │ (data/ folder)       │
          └──────────────────────┘
```

---

## 📈 주요 통계

| 항목 | 내용 |
|------|------|
| **언어** | Python 3.x |
| **프레임워크** | Streamlit (웹 UI) |
| **데이터 형식** | CSV (관계형 DB 미사용) |
| **AI 모델** | OpenAI (GPT-4o), Claude 3 (선택) |
| **팀 모듈** | 3개 (Purchasing, Logistics, Sales) |
| **페이지 수** | 3 페이지 + 1 홈 |
| **외부 API** | 5+ (OpenAI, Tavily, yfinance, NewsAPI, Frankfurter) |
| **핵심 기능** | ~15개 비즈니스 기능 |
| **내보내기 형식** | CSV, DOCX, XLSX |

---

## 🚧 개발 로드맵

### Phase 1 (현재)
- ✅ 기본 3모듈 통합 (Purchasing, Logistics, Sales)
- ✅ AI 기반 자동화 구현
- ✅ 실시간 데이터 연동

### Phase 2 (예정)
- [ ] 데이터베이스 마이그레이션 (CSV → PostgreSQL/MongoDB)
- [ ] 사용자 권한 관리 시스템
- [ ] 고급 보안 인증 (OAuth 2.0, JWT)
- [ ] 다국어 UI 지원

### Phase 3 (미래)
- [ ] 모바일 앱 개발
- [ ] 실시간 협업 기능
- [ ] 블록체인 기반 스마트 계약
- [ ] 예측 분석 대시보드

---

## 🤝 기여 가이드

프로젝트에 기여하고 싶으신 경우:
1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 라이선스

본 프로젝트는 교육 및 연구 목적으로 제작되었습니다.

---

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

---

## 🙏 Acknowledgments

- OpenAI for GPT-4o API
- Anthropic for Claude API
- Tavily for Search API
- Streamlit Community
- All data providers (HMM, LX Pantos, Glovis, etc.)

---

**© 2026 TradeNex - AI 기반 글로벌 무역 통합 시스템 v2.0**
