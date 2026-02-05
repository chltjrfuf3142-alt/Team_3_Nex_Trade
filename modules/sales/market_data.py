import yfinance as yf
import requests
import pandas as pd
import datetime

def get_market_indices():
    """실시간 지수 (현재가) 가져오기"""
    try:
        # 환율(KRW=X), 유가(CL=F) - 주가는 요청대로 제외
        tickers = ['KRW=X', 'CL=F']
        data = yf.download(tickers, period='1d', progress=False)
        
        # yfinance 버전 차이로 인한 데이터 구조 처리
        if 'Close' in data.columns:
            closes = data['Close']
            # 데이터가 1행일 경우 Series, 여러행일 경우 DataFrame 처리
            usd = closes['KRW=X'].iloc[-1] if 'KRW=X' in closes else 1380.0
            oil = closes['CL=F'].iloc[-1] if 'CL=F' in closes else 75.0
            return {"usd_krw": float(usd), "wti_oil": float(oil)}
            
        return {"usd_krw": 1380.0, "wti_oil": 75.0} # 기본값
    except Exception as e:
        print(f"Data Error: {e}")
        return {"usd_krw": 1380.0, "wti_oil": 75.0}

def get_exchange_rate_history():
    """[추가] 캔들 차트용 1달치 환율 데이터 가져오기"""
    try:
        # 1달치, 1일 간격
        df = yf.download('KRW=X', period='1mo', interval='1d', progress=False)
        return df
    except Exception:
        return pd.DataFrame()

def get_global_news(api_key):
    """뉴스 데이터 가져오기"""
    if not api_key: return []
    # 검색어: Korea Trade or Logistics (관련성 높임)
    url = f"https://newsapi.org/v2/everything?q=Korea Trade OR Logistics&sortBy=publishedAt&apiKey={api_key}&language=en"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return response.json().get('articles', [])[:5]
    except Exception:
        pass
    return []