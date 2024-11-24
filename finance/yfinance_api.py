import yfinance as yf

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