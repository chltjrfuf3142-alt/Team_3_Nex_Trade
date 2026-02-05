import pandas as pd
import os

class MarginCalculator:
    def __init__(self):
        # CSV 파일 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_path = os.path.join(current_dir, '..', '..', 'data', 'sales', 'margin.csv')
        self.margins = self.load_margins()

    def load_margins(self):
        try:
            df = pd.read_csv(self.csv_path)
            # 혹시 모를 공백 제거 (안전장치)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            # 비상용 기본 데이터 (파일 못 읽었을 때)
            return pd.DataFrame({
                "Category_Code": ["GEN", "FUN", "PRE"],
                "Margin_Rate": [0.28, 0.45, 0.96],
                "Logic_Summary": ["기본", "기능성", "프리미엄"],
                "Benchmark_Company": ["Default", "Default", "Default"],
                "Category_Name": ["General", "Functional", "Premium"]
            })

    def calculate_price(self, cost, category_code):
        """원가와 카테고리 코드를 받아 판매가 계산"""
        # [수정] 실제 CSV 컬럼명인 'Category_Code' 사용
        row = self.margins[self.margins['Category_Code'] == category_code]
        
        if row.empty:
            return cost * 1.2, 20.0, "기본 마진 (데이터 없음)"
        
        # [수정] 'Margin_Rate', 'Logic_Summary' 등 실제 컬럼명 매칭
        raw_rate = row.iloc[0]['Margin_Rate'] # 예: 0.28
        desc = row.iloc[0]['Logic_Summary']
        company = row.iloc[0]['Benchmark_Company']
        
        # 마진율 계산 (0.28 -> 28%)
        if raw_rate < 1.0: 
            rate_percent = raw_rate * 100
            sales_price = cost * (1 + raw_rate)
        else:
            rate_percent = raw_rate
            sales_price = cost * (1 + raw_rate / 100)
            
        return sales_price, rate_percent, f"{desc} ({company} 기준)"