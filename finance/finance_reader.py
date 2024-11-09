import stock_code_lookup as scl
import yfinance_api as ya
import pandas as pd

def main():
    market_type = input('시장 유형을 선택하세요 (국내/국외): ')
    if market_type == '국내':
        company_name = input('기업명을 입력하세요: ')
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
    elif market_type == '국외':
        company_name = input('기업명을 입력하세요: ')
        stock_code = scl.get_us_stock_code(company_name)

        if stock_code:
            print(f"{company_name}의 종목 코드는 {stock_code} 입니다.")
        else:
            print(f"{company_name}의 종목 코드를 찾을 수 없습니다.")
            return
    else:
        print('잘못된 입력입니다.')
        return

    ya.print_recent_data(stock_code)

if __name__ == '__main__':
    main()
