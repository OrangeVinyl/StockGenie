import FinanceDataReader as fdr

def get_stock_code(company_name):
    df_krx = fdr.StockListing('KRX')
    result = df_krx[df_krx['Name'] == company_name]

    if not result.empty:
        return result.iloc[0]['Code']
    else:
        return None

def main():
    company_name = input('기업명을 입력하세요 : ')
    stock_code = get_stock_code(company_name)

    if stock_code:
        print(f"{company_name}의 종목 코드는 {stock_code} 입니다.")
    else:
        print(f"{company_name}의 종목 코드를 찾을 수 없습니다.")


if __name__ == '__main__':
    main()