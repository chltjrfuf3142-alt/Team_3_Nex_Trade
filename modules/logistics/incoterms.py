# modules/incoterms.py

class IncotermManager:
    """
    인코텀즈 2020 + Legacy(DDU, DAT) 총 13가지 조건별 비용 분장 로직
    """
    def calculate_breakdown(self, term, base_data):
        """
        base_data: {mfg_cost, inland, thc, ocean, rail, insurance, duty, margin}
        """
        # 공통 비용 추출
        costs = {"1.Product Cost": base_data['mfg_cost']}
        
        # --- Group E (Departure) ---
        if term == "EXW":
            return costs # 원가 끝
            
        # --- Group F (Main Carriage Unpaid) ---
        # FCA, FAS, FOB
        if term in ["FCA", "FAS", "FOB"]:
            costs["2.Inland(KR)"] = base_data['inland']
            costs["3.Export Clearance"] = 50 # 수출통관비
            if term != "FCA":
                costs["4.THC(Loading)"] = base_data['thc']
            costs["5.Handling Fee"] = base_data['margin'] * 0.5 # 마진 일부
            return costs

        # --- Group C (Main Carriage Paid) ---
        # CFR, CIF, CPT, CIP
        if term in ["CFR", "CIF", "CPT", "CIP"]:
            costs["2.Inland(KR)"] = base_data['inland']
            costs["3.THC(Loading)"] = base_data['thc']
            costs["4.Export Clearance"] = 50
            costs["5.Ocean Freight"] = base_data['ocean']
            costs["6.Handling Fee"] = base_data['margin']
            
            if term in ["CIF", "CIP"]:
                costs["7.Insurance"] = base_data['insurance']
            return costs

        # --- Group D (Arrival) ---
        # DAP, DPU, DDP, DAT(Old), DDU(Old)
        if term in ["DAP", "DPU", "DDP", "DAT", "DDU"]:
            costs["2.Inland(KR)"] = base_data['inland']
            costs["3.THC(Loading)"] = base_data['thc']
            costs["4.Export Clearance"] = 50
            costs["5.Ocean Freight"] = base_data['ocean']
            costs["6.Handling Fee"] = base_data['margin']
            
            # D조건은 보통 보험 포함 관행 (DDU, DAP 제외하곤)
            if term not in ["DDU", "DAP"]:
                costs["7.Insurance"] = base_data['insurance']
            
            # 내륙 운송 (Rail) 추가
            costs["8.Rail Freight(TCR)"] = base_data['rail']
            
            # 도착지 하역 (DPU, DAT, DDP)
            if term in ["DPU", "DAT", "DDP"]:
                costs["9.Dest Unloading"] = base_data['thc']
            
            # 관세 (DDP Only)
            if term == "DDP":
                costs["10.Duty & Tax"] = base_data['duty']
                
            return costs
            
        return costs # Default