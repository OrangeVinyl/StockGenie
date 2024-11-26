import os
from . import stock_ticker as scl
from . import yfinance_reader as ya

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(BASE_DIR, '../data/stock_dataset')


def decide_stock_market(market_type, company_name):
    if market_type == '국내':
        stock_code, market = scl.get_domestic_stock_code(company_name)

        if stock_code:
            if market == 'KOSPI':
                stock_code += '.KS'
            elif market == 'KOSDAQ':
                stock_code += '.KQ'
            else:
                stock_code += '.KS'

            print(f"{company_name}의 종목 코드는 {stock_code} 입니다.")
        else:
            print(f"{company_name}의 종목 코드를 찾을 수 없습니다.")
            return
    elif market_type == '해외':
        stock_code = scl.get_us_stock_code(company_name)

        if stock_code:
            print(f"{company_name}의 종목 코드는 {stock_code} 입니다.")
        else:
            print(f"{company_name}의 종목 코드를 찾을 수 없습니다.")
            return
    else:
        print('잘못된 입력입니다.')
        return

    data = ya.print_recent_data(stock_code)

    save_file = os.path.join(SAVE_PATH, f"{company_name}_stock_dataset.csv")
    data.to_csv(save_file)

def test_stock_market():
    decide_stock_market('해외', 'Intel')