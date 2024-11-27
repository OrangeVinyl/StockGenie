import re
import difflib
import pandas as pd
import FinanceDataReader as fdr

DOMESTIC_MARKET_LIST = ['KRX']
US_MARKET_LIST = ['NASDAQ', 'NYSE', 'AMEX']
CLOSE_MATCHES_LIMIT = 5
CLOSE_MATCHES_CUTOFF = 0.5

def preprocess_name(name):
    """
    @description: 기업명을 전처리하는 함수
    - 영어, 숫자, 한글만 남기고 소문자로 변환
    - 특수문자 제거

    :param name:
    :return:
    """
    return re.sub(r'[^A-Za-z0-9가-힣]', '', name).lower()

def suggest_close_matches(company_name, name_list):
    """
    @description: 입력한 기업명에 대해 유사한 기업명을 제안하는 함수

    :param company_name:
    :param name_list:
    """
    close_matches = difflib.get_close_matches(company_name, name_list, n=CLOSE_MATCHES_LIMIT, cutoff=CLOSE_MATCHES_CUTOFF)
    if close_matches:
        print(f"'{company_name}'를 찾을 수 없습니다. 혹시 다음 기업 중 하나를 찾으시나요?")
        for name in close_matches:
            print(f"- {name}")

def load_stock_listing(market):
    """
    @description: 지정된 시장의 주식 목록을 로드합니다.

    :param market: str - 시장 (KRX, NASDAQ, NYSE, AMEX)
    """
    try:
        df = fdr.StockListing(market)
        df['Name_processed'] = df['Name'].apply(preprocess_name)
        return df
    except Exception as e:
        print(f"[ERROR] {market} 시장의 주식 목록을 로드하는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

def load_us_stock_listing():
    """
    @description: 해외(미국) 시장(NASDAQ, NYSE, AMEX)의 주식 목록을 로드하고 병합하는 함수

    :return: DataFrame
    """
    df_list = []
    for market in US_MARKET_LIST:
        df = load_stock_listing(market)
        if not df.empty:
            df['Market'] = market
            df_list.append(df)

    if df_list:
        df_us = pd.concat(df_list, ignore_index=True)
        df_us = df_us.drop_duplicates(subset='Symbol')
        return df_us
    else:
        return pd.DataFrame()

def get_domestic_stock_code(company_name):
    """
    @description: 국내 시장의 주식 코드를 찾는 함수

    :param company_name:
    :return:
    """
    df_krx = load_stock_listing('KRX')
    if df_krx.empty:
        print("[WARN] KRX 시장의 데이터를 불러오는 데 실패했습니다.")
        return None, None

    company_name_processed = preprocess_name(company_name)
    matches = df_krx[df_krx['Name_processed'].str.contains(company_name_processed)]

    if not matches.empty:
        return matches.iloc[0]['Code'], matches.iloc[0]['Market']
    else:
        suggest_close_matches(company_name, df_krx['Name'].tolist())
        return None, None

def get_us_stock_code(company_name):
    """
    @description: 미국 시장의 주식 코드를 찾는 함수

    :param company_name:
    :return:
    """
    df_us = load_us_stock_listing()
    if df_us.empty:
        print("[WARN] 미국 시장의 데이터를 불러오는 데 실패했습니다.")
        return None

    company_name_processed = preprocess_name(company_name)
    matches = df_us[df_us['Name_processed'].str.contains(company_name_processed)]

    if not matches.empty:
        return matches.iloc[0]['Symbol']
    else:
        suggest_close_matches(company_name, df_us['Name'].tolist())
        return None

def test_stock_ticker():
    # 국내 시장 테스트 예시
    domestic_code, domestic_market = get_domestic_stock_code('삼성전자')
    if domestic_code:
        print(f"삼성전자의 종목 코드는 {domestic_code} ({domestic_market}) 입니다.")

    # 해외 시장 테스트 예시
    us_code = get_us_stock_code('Intel')
    if us_code:
        print(f"Intel의 종목 코드는 {us_code} 입니다.")