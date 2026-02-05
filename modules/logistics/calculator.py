import pandas as pd
import os

class LogisticsCalculator:
    """
    [물류비 연산 엔진 v2.0]
    기본 운임에 BAF(유가할증), CAF(통화할증) 등 현실적인 변수를 적용합니다.
    """
    def __init__(self):
        # 1. 현재 이 파일(calculator.py)이 있는 폴더 위치를 찾습니다.
        # 위치: TradeNex/modules/logistics
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 2. 프로젝트의 가장 위쪽 폴더(TradeNex)를 찾으러 두 단계 올라갑니다.
        # modules/logistics (현재) -> modules (1단계 위) -> TradeNex (2단계 위)
        root_dir = os.path.dirname(os.path.dirname(current_dir))

        # 3. 데이터가 들어있는 폴더를 정확히 지정합니다.
        # 목표: TradeNex/data/logistics
        self.base_path = os.path.join(root_dir, 'data', 'logistics')

        # 4. 데이터 로드 (이제 경로가 정확해서 잘 찾아옵니다!)
        self.hmm_df = self._load_csv('hmm_shipping_data.csv')
        self.lx_inland_df = self._load_csv('lx_inland.csv')
        self.glovis_df = self._load_csv('glocis_handle_data.csv')

    def _load_csv(self, filename):
        # ... (이 아래 코드는 보내주신 그대로 두시면 됩니다!) ...
        path = os.path.join(self.base_path, filename)
        if os.path.exists(path):
            return pd.read_csv(path)
        return None

    def get_base_costs(self, route_type, teus=1):
        # 1. 거리 및 루트 설정
        if "Mongolia" in route_type:
            rail_dist = 1800 
        else:
            rail_dist = 4500 

        # 2. 데이터 추출 (기본값 Fallback)
        try:
            # HMM 운임 (2025 3Q 기준)
            ocean_rate = float(self.hmm_df.loc[self.hmm_df['Route'] == 'Asia-Europe', 'Price_2025_3Q'].values[0])
        except: ocean_rate = 1481

        try:
            # LX 철도 운임
            rail_rate_per_km = float(self.lx_inland_df.loc[self.lx_inland_df['Item'] == 'Rail_Unit_Price_TCR', 'Value'].values[0])
        except: rail_rate_per_km = 0.75

        try:
            # Glovis 마진 & 환율
            margin_rate = float(self.glovis_df.loc[self.glovis_df['Item'] == 'Logistics_Margin', 'Value'].values[0]) / 100
            exchange_rate = float(self.glovis_df.loc[self.glovis_df['Item'] == 'Exchange_Rate', 'Value'].values[0])
        except: 
            margin_rate = 0.045
            exchange_rate = 1380

        # [UPGRADE] 현실적인 할증료(Surcharge) 로직 추가
        # BAF(유가할증료): 해상 운임의 10% 가정
        baf_factor = 1.10 
        # CAF(통화할증료): 환율 변동 리스크 5% 가정
        caf_factor = 1.05 
        # PSS(성수기 할증): 3분기는 물류 성수기이므로 15% 할증
        pss_factor = 1.15

        # 3. 최종 비용 계산 (할증 적용)
        # 해상운임에는 유가/통화/성수기 할증이 모두 붙음
        ocean_cost = (ocean_rate * baf_factor * caf_factor * pss_factor) * teus
        
        # 철도운임은 유가 할증 정도만 반영
        rail_cost = (rail_dist * rail_rate_per_km * baf_factor) * teus
        
        inland_kr_cost = 400 * teus
        thc_cost = 150 * teus

        return {
            "ocean_cost": ocean_cost,
            "rail_cost": rail_cost,
            "inland_kr_cost": inland_kr_cost,
            "thc_cost": thc_cost,
            "margin_rate": margin_rate,
            "exchange_rate": exchange_rate
        }