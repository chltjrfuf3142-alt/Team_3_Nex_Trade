import os
import sys
import requests
import urllib.parse

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from config import get_env

def get_hs_code(keyword):
    """
    관세청 HS부호 조회 API 호출
    """
    # [내장된 표준 URL]
    url = "https://apis.data.go.kr/1220000/retrieveHsCode/getHsCodeList"

    # 클라우드 + 로컬 환경 지원
    service_key = get_env("HS_SEARCH_API")
    
    if not service_key:
        return {"error": "HS_SEARCH_API 키가 없습니다."}

    # 키 디코딩 (공공데이터포털 키 오류 방지)
    try:
        decoded_key = urllib.parse.unquote(service_key)
    except:
        decoded_key = service_key

    # 요청 파라미터
    params = {
        "serviceKey": decoded_key,
        "hsSgn": keyword, # 품목명 또는 HS코드
        "pageNo": "1",
        "numOfRows": "5"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # 데이터 구조가 복잡할 수 있어 'data' 항목만 리턴하거나 전체 리턴
            return data.get('data', []) 
        else:
            return []
    except Exception as e:
        return []

def get_tariff_rate(hs_code):
    """
    관세율 조회 API 호출
    """
    url = "https://apis.data.go.kr/1220000/retrieveTariff/getTariffList"
    service_key = get_env("RATE_BASIC_API")
    
    if not service_key:
        return None
        
    try:
        decoded_key = urllib.parse.unquote(service_key)
        params = {
            "serviceKey": decoded_key,
            "hsSgn": hs_code,
            "pageNo": "1",
            "numOfRows": "5"
        }
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get('data', [])
        return None
    except:
        return None