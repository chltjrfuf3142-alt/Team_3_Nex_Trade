"""
실시간 대시보드 데이터 조회 모듈
- 환율 조회 (ExchangeRate-API + yfinance)
- 뉴스 조회 (NewsAPI + 한글 번역)
- 캔들스틱 차트 생성
"""

import os
import sys
from datetime import date
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import requests
from deep_translator import GoogleTranslator

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from config import get_env


def fetch_exchange_rate():
    """ExchangeRate-API를 통해 실시간 환율 가져오기"""
    api_key = get_env("EXCHANGE_RATE_KEY")

    if not api_key:
        return None, "API 키 없음"

    try:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get('result') == 'success':
            krw_rate = data['conversion_rates']['KRW']
            return krw_rate, "Success"
        else:
            return None, data.get('error-type', 'Unknown error')
    except Exception as e:
        return None, str(e)


@st.cache_data(ttl=600)
def fetch_news():
    """NewsAPI를 통해 실시간 무역/금융 뉴스 가져오기 (한글 번역)"""
    api_key = get_env("NEWS_API_KEY")

    if not api_key:
        # API 키 없을 때 더미 데이터
        return [
            {"title": "K-푸드 글로벌 수출 역대 최고치 달성", "source": "Global Trade News", "date": str(date.today()), "url": "#"},
            {"title": "해상 운임 안정화 추세, 물류비 절감 기대", "source": "Logistics World", "date": str(date.today()), "url": "#"},
            {"title": "달러 강세 지속, 수출 경쟁력 상승", "source": "Bloomberg", "date": str(date.today()), "url": "#"},
            {"title": "신흥국 프리미엄 소비재 시장 급성장", "source": "Market Watch", "date": str(date.today()), "url": "#"}
        ]

    try:
        # 무역/금융 관련 키워드로 검색
        url = "https://newsapi.org/v2/everything"
        params = {
            "apiKey": api_key,
            "q": "trade OR export OR finance OR economy",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5
        }

        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if data.get('status') == 'ok':
            articles = []
            translator = GoogleTranslator(source='en', target='ko')

            for article in data.get('articles', [])[:5]:
                title_en = article.get('title', 'No title')

                # 영문 제목을 한글로 번역
                try:
                    title_ko = translator.translate(title_en)
                except:
                    title_ko = title_en  # 번역 실패시 원문 사용

                articles.append({
                    "title": title_ko,
                    "source": article.get('source', {}).get('name', 'Unknown'),
                    "date": article.get('publishedAt', '')[:10],
                    "url": article.get('url', '#')
                })
            return articles
        else:
            return []
    except Exception as e:
        st.warning(f"뉴스 로딩 실패: {e}")
        return []


@st.cache_data(ttl=600)
def fetch_dashboard_data():
    """대시보드용 모든 데이터 통합 조회"""
    data = {
        "exchange": {"current": 1460.1, "history": pd.DataFrame(), "change": 0, "change_pct": 0},
        "oil": {"current": 61.52, "history": pd.DataFrame(), "change": 0, "change_pct": 0},
        "news": []
    }

    # 1. 환율 (ExchangeRate-API 우선, yfinance 백업)
    rate, status = fetch_exchange_rate()
    if rate:
        data["exchange"]["current"] = rate

    # yfinance로 환율 히스토리 가져오기
    try:
        ex_ticker = yf.Ticker("KRW=X")
        ex_hist = ex_ticker.history(period="1mo")
        if not ex_hist.empty:
            data["exchange"]["history"] = ex_hist
            data["exchange"]["current"] = ex_hist['Close'].iloc[-1]
            if len(ex_hist) > 1:
                data["exchange"]["change"] = ex_hist['Close'].iloc[-1] - ex_hist['Close'].iloc[-2]
                data["exchange"]["change_pct"] = (data["exchange"]["change"] / ex_hist['Close'].iloc[-2]) * 100
    except:
        pass

    # 2. 유가 (yfinance)
    try:
        oil_ticker = yf.Ticker("CL=F")
        oil_hist = oil_ticker.history(period="1mo")
        if not oil_hist.empty:
            data["oil"]["history"] = oil_hist
            data["oil"]["current"] = oil_hist['Close'].iloc[-1]
            if len(oil_hist) > 1:
                data["oil"]["change"] = oil_hist['Close'].iloc[-1] - oil_hist['Close'].iloc[-2]
                data["oil"]["change_pct"] = (data["oil"]["change"] / oil_hist['Close'].iloc[-2]) * 100
    except:
        pass

    # 3. 뉴스
    data["news"] = fetch_news()

    return data


def draw_candlestick_chart(df):
    """전통적인 캔들스틱 차트 (상승=빨강, 하락=파랑)"""
    if df is None or df.empty:
        return go.Figure()

    # 최근 30일 데이터 사용 (14일 → 30일로 증가)
    df_recent = df.tail(30) if len(df) > 30 else df

    # OHLC 데이터가 있는지 확인
    has_ohlc = all(col in df_recent.columns for col in ['Open', 'High', 'Low', 'Close'])

    if not has_ohlc:
        # OHLC가 없으면 Close만 사용한 간단한 차트
        df_recent = df_recent.copy()
        df_recent['Open'] = df_recent['Close']
        df_recent['High'] = df_recent['Close']
        df_recent['Low'] = df_recent['Close']

    # 데이터 범위 계산
    y_min = df_recent['Low'].min()
    y_max = df_recent['High'].max()
    y_range = y_max - y_min
    y_padding = y_range * 0.15

    fig = go.Figure()

    # 각 캔들 그리기
    for i, idx in enumerate(df_recent.index):
        row = df_recent.loc[idx]

        # 상승/하락 판단
        is_up = row['Close'] >= row['Open']
        candle_color = '#EF4444' if is_up else '#3B82F6'  # 빨강/파랑
        fill_opacity = 0.9

        # 1. 심지 (High-Low 선)
        fig.add_trace(go.Scatter(
            x=[idx, idx],
            y=[row['Low'], row['High']],
            mode='lines',
            line=dict(color=candle_color, width=1.5),
            showlegend=False,
            hoverinfo='skip'
        ))

        # 2. 몸통 (Open-Close 박스)
        body_height = abs(row['Close'] - row['Open'])
        body_y = min(row['Open'], row['Close'])

        # 몸통이 너무 작으면 최소 높이 설정
        if body_height < y_range * 0.002:
            body_height = y_range * 0.002

        # 캔들 너비 계산 (시간 간격에 따라 자동 조정)
        if len(df_recent) > 1:
            time_diff = (df_recent.index[1] - df_recent.index[0]).total_seconds() / 3600 / 24
            candle_width = pd.Timedelta(days=time_diff * 0.4)  # 0.6 → 0.4로 줄임
        else:
            candle_width = pd.Timedelta(hours=8)  # 12 → 8로 줄임

        fig.add_shape(
            type="rect",
            x0=idx - candle_width,
            x1=idx + candle_width,
            y0=body_y,
            y1=body_y + body_height,
            fillcolor=candle_color,
            line=dict(color=candle_color, width=1),
            opacity=fill_opacity
        )

    # 호버 정보를 위한 투명 포인트
    fig.add_trace(go.Scatter(
        x=df_recent.index,
        y=df_recent['Close'],
        mode='markers',
        marker=dict(size=0.1, color='rgba(0,0,0,0)'),
        showlegend=False,
        hovertemplate=(
            '시가: %{customdata[0]:,.2f}<br>'
            '고가: %{customdata[1]:,.2f}<br>'
            '저가: %{customdata[2]:,.2f}<br>'
            '종가: %{y:,.2f}<extra></extra>'
        ),
        customdata=df_recent[['Open', 'High', 'Low']].values
    ))

    # 추세선 추가 (가는 파란색 선)
    fig.add_trace(go.Scatter(
        x=df_recent.index,
        y=df_recent['Close'],
        mode='lines',
        line=dict(
            color='rgba(99, 102, 241, 0.5)',  # 은은한 파란색
            width=1.5,
            dash='solid'
        ),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig.update_layout(
        xaxis=dict(
            visible=True,
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
            gridwidth=1,
            showline=True,
            linecolor='rgba(200, 200, 200, 0.3)',
            linewidth=1,
            tickfont=dict(size=9, color='#64748B'),
            tickformat='%m/%d'
        ),
        yaxis=dict(
            visible=True,
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
            gridwidth=1,
            showline=True,
            linecolor='rgba(200, 200, 200, 0.3)',
            linewidth=1,
            tickfont=dict(size=9, color='#64748B'),
            side='right',
            range=[y_min - y_padding, y_max + y_padding]
        ),
        margin=dict(l=5, r=40, t=5, b=30),
        height=150,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.5)',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="white",
            font_size=11,
            font_family="Pretendard, sans-serif"
        )
    )

    return fig


def generate_analysis(data_type, change_pct):
    """변화율에 따른 분석 코멘트"""
    if data_type == "exchange":
        if change_pct > 0:
            return f"원화 약세 지속 (+{change_pct:.1f}%)\n원달러 환율이 전일보다 상승했습니다."
        else:
            return f"원화 강세 지속 ({change_pct:.1f}%)\n원달러 환율이 전일보다 하락했습니다."
    else:  # oil
        if change_pct > 0:
            return f"유가 상승세 (+{change_pct:.1f}%)\n국제 유가가 전일보다 상승했습니다."
        else:
            return f"유가 하락세 ({change_pct:.1f}%)\n국제 유가가 전일보다 하락했습니다."
