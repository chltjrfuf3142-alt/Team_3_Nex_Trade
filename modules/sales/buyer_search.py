"""
바이어 검색 및 생성 모듈
- 국가별 회사 스타일 정보 제공
- 더미 바이어 데이터 생성
- 실제 DB 및 더미 데이터 혼합 조회
"""

import os
import random
import pandas as pd


def get_country_style(country_name):
    """국가별 회사명 스타일 및 지역 정보 반환"""
    c = country_name.lower()
    if "일본" in c or "japan" in c:
        return {
            "suffix": ["Co., Ltd.", "K.K.", "Corporation", "Group"],
            "cities": ["Tokyo", "Osaka", "Nagoya", "Fukuoka"],
            "domain": "co.jp"
        }
    elif "브라질" in c or "brazil" in c:
        return {
            "suffix": ["Ltda.", "S.A.", "Eireli", "Comércio"],
            "cities": ["Sao Paulo", "Rio de Janeiro", "Brasilia"],
            "domain": "com.br"
        }
    elif "독일" in c or "germany" in c:
        return {
            "suffix": ["GmbH", "AG", "KG", "International"],
            "cities": ["Berlin", "Munich", "Frankfurt", "Hamburg"],
            "domain": "de"
        }
    elif "베트남" in c or "vietnam" in c:
        return {
            "suffix": ["JSC", "Co., Ltd", "Trading", "Vina Corp"],
            "cities": ["Ho Chi Minh", "Hanoi", "Da Nang"],
            "domain": "vn"
        }
    elif "영국" in c or "uk" in c or "britain" in c:
        return {
            "suffix": ["Ltd.", "PLC", "Group", "Holdings"],
            "cities": ["London", "Manchester", "Liverpool"],
            "domain": "co.uk"
        }
    else:
        return {
            "suffix": ["Inc.", "Corp", "Group", "Trading"],
            "cities": ["Capital City", "Port City", "Central District"],
            "domain": "com"
        }


def generate_dummy_buyer(product, country, buyer_id=100):
    """더미 바이어 정보 생성"""
    style = get_country_style(country)

    prefix = random.choice(["Global", "National", "Royal", "Prime", "First", "Star", "Golden", "United"])
    if random.random() > 0.5:
        city_prefix = random.choice(style["cities"])
        comp_name = f"{city_prefix} {product.capitalize()} {random.choice(style['suffix'])}"
    else:
        comp_name = f"{prefix} {product.capitalize()} {random.choice(style['suffix'])}"

    clean_name = comp_name.split(' ')[0].lower()
    email = f"info@{clean_name}.{style['domain']}"

    cap = f"{random.randint(5, 200)}M USD"
    founded = random.randint(1985, 2021)
    desc = f"{country} 내 {product} 시장을 선도하는 유력 유통 기업입니다."

    return {
        "id": buyer_id, "Name": comp_name, "Business": "Import & Dist.",
        "Founded": founded, "Revenue": cap, "Profit": "N/A",
        "Desc": desc, "Email": email, "Country": country
    }


def fetch_buyer_list(product, country):
    """제품과 국가에 맞는 바이어 리스트 반환 (실제 DB + 더미 데이터)"""
    results = []
    norm_p = product.replace(" ", "").lower()
    norm_c = country.replace(" ", "").lower()

    target_keywords = ["건강", "기능", "보조", "식품", "샘물", "생수", "물", "음료",
                       "자양", "수액", "비타민", "홍삼", "마시는", "화장품"]
    is_mongol = "몽골" in norm_c or "mongol" in norm_c
    is_target_prod = any(k in norm_p for k in target_keywords)

    # 몽골 + 건강식품이면 실제 DB 로드
    if is_mongol and is_target_prod:
        try:
            # 경로 설정
            current_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(os.path.dirname(current_dir))
            buyers_file = os.path.join(root_dir, "data", "sales", "global_buyers.csv")

            df = pd.read_csv(buyers_file)
            df.columns = df.columns.str.strip()
            for _, row in df.iterrows():
                results.append({
                    "id": row['id'], "Name": row['Name'], "Business": row['Business'],
                    "Founded": row['Founded'], "Revenue": row.get('Capital', 'N/A'), "Profit": "N/A",
                    "Desc": row['Description'], "Email": row['Email'], "Country": row['Country']
                })
        except:
            pass

    # 부족하면 더미 생성
    current_count = len(results)
    needed = 10 - current_count

    if needed > 0:
        start_id = current_count + 100
        for i in range(needed):
            results.append(generate_dummy_buyer(product, country, start_id + i))

    return results
