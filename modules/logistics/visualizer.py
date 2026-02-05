import pydeck as pdk
import plotly.graph_objects as go
import os

def render_3d_route(path_ocean, path_inland, path_rail, view_state):
    """
    3D 지도 렌더링 엔진 (Tooltip 기능 강화 버전)
    - 마우스 호버 시 경로 이름 표시 (pickable=True, tooltip 설정)
    """
    
    # 1. 레이어 정의
    layers = [
        # (1) 해상 경로 (파란색)
        pdk.Layer(
            "PathLayer",
            # data에 'name' 필드를 추가해야 툴팁에 뜹니다.
            data=[{"path": path_ocean, "name": "🚢 Sea Transport: Incheon → Lianyungang"}],
            get_path="path",
            get_color=[30, 144, 255, 200], # Blue
            get_width=40000,
            width_min_pixels=3,
            pickable=True,       # <--- [핵심] 마우스 반응 켜기
            auto_highlight=True  # 마우스 올리면 밝게 빛남
        ),
        
        # (2) 내륙 경로 (초록색)
        pdk.Layer(
            "PathLayer",
            data=[{"path": path_inland, "name": "🚛 Inland Transport: Port → Hub"}],
            get_path="path",
            get_color=[67, 160, 71, 200], # Green
            get_width=35000,
            width_min_pixels=3,
            pickable=True,       # <--- [핵심]
            auto_highlight=True
        ),
        
        # (3) 철도 경로 (빨간색)
        pdk.Layer(
            "PathLayer",
            data=[{"path": path_rail, "name": "🚂 Rail Transport: Cross-Border Rail"}],
            get_path="path",
            get_color=[220, 20, 60, 200], # Red
            get_width=40000,
            width_min_pixels=3,
            pickable=True,       # <--- [핵심]
            auto_highlight=True
        ),

        # (4) 텍스트/아이콘 레이어 (클릭 방해 안 되게 pickable=False 추천, 원하면 True)
        pdk.Layer(
            "TextLayer",
            data=[
                {"pos": path_ocean[0], "t": "🇰🇷 Incheon"},
                {"pos": path_rail[-1], "t": "🏁 Destination"}
            ],
            get_position="pos",
            get_text="t",
            get_color=[255, 255, 255],
            get_size=18,
            get_alignment_baseline="'bottom'",
            pickable=False 
        )
    ]

    # 2. Deck 렌더링 설정
    return pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        # [핵심] 토큰 없는 다크맵 스타일 고정
        map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        # [핵심] 툴팁 설정: data 안의 'name'을 보여줘라
        tooltip={
            "html": "<b>{name}</b>",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white"
            }
        }
    )

def draw_cost_waterfall(breakdown, total_price):
    """물류비 Waterfall 차트 (기존 유지)"""
    fig = go.Figure(go.Waterfall(
        orientation="v", 
        measure=["relative"] * len(breakdown) + ["total"],
        x=list(breakdown.keys()) + ["Total"], 
        y=list(breakdown.values()) + [total_price],
        text=[f"${v:,.0f}" for v in breakdown.values()] + [f"${total_price:,.0f}"],
        connector={"line": {"color": "#333"}},
        totals={"marker": {"color": "#ef553b"}},
        decreasing={"marker": {"color": "#00cc96"}},
        increasing={"marker": {"color": "#1f77b4"}},
    ))
    
    fig.update_layout(
        height=450, 
        margin=dict(t=20, b=20, l=10, r=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="black") # 차트 글씨 잘 보이게
    )
    return fig