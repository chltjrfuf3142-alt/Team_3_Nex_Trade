# config.py

import os
import streamlit as st
from dotenv import load_dotenv

# .env 파일 로드 (로컬 환경용)
load_dotenv()

def get_env(key: str, default: str = None) -> str:
    """
    환경변수를 가져오는 헬퍼 함수
    - 클라우드 배포: st.secrets 사용
    - 로컬 개발: os.getenv 사용
    """
    # 1. Streamlit Cloud secrets 확인
    try:
        if key in st.secrets:
            return st.secrets[key]
    except:
        pass

    # 2. 로컬 환경변수 확인
    return os.getenv(key, default)

# 1. 현재 파일(config.py)이 있는 위치 (TradeNex 루트)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 데이터 폴더 경로 설정 (data/logistics)
# 🚨 물류팀 데이터가 'data/logistics' 안에 있다고 가정합니다.
DATA_DIR = os.path.join(BASE_DIR, 'data', 'logistics')

# 3. 기본값 (Fallback Data)
DEFAULT_RATES = {
    "ocean_teu": 1481,  # HMM
    "rail_km": 0.75,    # LX Pantos
    "margin": 0.045,    # Glovis
    "exchange": 1380,   # KRW/USD
    "duty_mn": 8.0,     # Mongolia Tariff
    "duty_kz": 8.0,     # Kazakhstan Tariff
    "insurance": 0.003  # 0.3%
}

# 4. 좌표 정보 (Map Logic)
COORDINATES = {
    "Incheon": [126.7052, 37.4563],
    "Lianyungang": [119.4363, 34.7466],
    "Mongolia": [106.9176, 47.9188],
    "Kazakhstan": [76.8512, 43.2220]
}