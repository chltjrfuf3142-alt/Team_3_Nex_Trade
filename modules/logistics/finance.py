import requests

def get_realtime_exchange_rate(base="USD", target="KRW"):
    """무료 API를 통한 실시간 환율 조회"""
    try:
        url = f"https://api.frankfurter.app/latest?from={base}&to={target}"
        res = requests.get(url, timeout=2)
        return res.json()['rates'][target]
    except:
        return 1380.0  # API 실패 시 고정 환율 반환