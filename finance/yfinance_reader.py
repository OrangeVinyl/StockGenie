import os
import yfinance as yf
from datetime import datetime, timedelta

def get_stock_history(stock_code, period="1y"):
    ticker = yf.Ticker(stock_code)
    hist = ticker.history(period=period)
    return hist

def print_recent_data(stock_code, days=20):
    hist = get_stock_history(stock_code)
    if not hist.empty:
        print(f"{stock_code}의 최근 {days}일간 주가 데이터:")
        print(hist.tail(days))
    else:
        print(f"{stock_code}에 대한 데이터를 가져올 수 없습니다.")

    return hist


def get_stock_data(company_name):
    """
    @description finance를 사용하여 주가 데이터를 가져와 CSV로 저장하고 DataFrame으로 반환하는 함수
    - 데이터는 1년치 데이터를 기준

    :param company_name:
    """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)

    ticker = yf.Ticker(company_name)
    stock_df = ticker.history(start=start_date, end=end_date)
    stock_df.reset_index(inplace=True)

    # CSV 저장
    csv_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    stock_csv_folder_path = os.path.join(csv_dir, 'data', 'stocks')
    os.makedirs(stock_csv_folder_path, exist_ok=True)
    stock_csv_data = os.path.join(stock_csv_folder_path, f"{company_name}_stock_dataset.csv")
    stock_df.to_csv(stock_csv_data, index=False)

    return stock_df