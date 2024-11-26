import re
import difflib
import pandas as pd
import FinanceDataReader as fdr

df_krx = None
df_us = None

def preprocess_name(name):
    return re.sub(r'[^A-Za-z0-9가-힣]', '', name).lower()

def get_domestic_stock_code(company_name):
    global df_krx
    if df_krx is None:
        df_krx = fdr.StockListing('KRX')
        df_krx['Name_processed'] = df_krx['Name'].apply(preprocess_name)

    company_name_processed = preprocess_name(company_name)
    matches = df_krx[df_krx['Name_processed'].str.contains(company_name_processed)]

    if not matches.empty:
        return matches.iloc[0]['Code'], matches.iloc[0]['Market']
    else:
        names = df_krx['Name'].tolist()
        close_matches = difflib.get_close_matches(company_name, names, n=5, cutoff=0.5)
        if close_matches:
            print(f"'{company_name}'를 찾을 수 없습니다. 혹시 다음 기업 중 하나를 찾으시나요?")
            for name in close_matches:
                print(f"- {name}")
        return None, None

def get_us_stock_code(company_name):
    global df_us
    if df_us is None:
        nasdaq = fdr.StockListing('NASDAQ')
        nasdaq['Market'] = 'NASDAQ'

        nyse = fdr.StockListing('NYSE')
        nyse['Market'] = 'NYSE'

        amex = fdr.StockListing('AMEX')
        amex['Market'] = 'AMEX'

        df_us = pd.concat([nasdaq, nyse, amex])
        df_us = df_us.drop_duplicates('Symbol')
        df_us['Name_processed'] = df_us['Name'].apply(preprocess_name)

    company_name_processed = preprocess_name(company_name)
    matches = df_us[df_us['Name_processed'].str.contains(company_name_processed)]

    if not matches.empty:
        return matches.iloc[0]['Symbol']
    else:
        names = df_us['Name'].tolist()
        close_matches = difflib.get_close_matches(company_name, names, n=5, cutoff=0.5)
        if close_matches:
            print(f"'{company_name}'를 찾을 수 없습니다. 혹시 다음 기업 중 하나를 찾으시나요?")
            for name in close_matches:
                print(f"- {name}")
        return None