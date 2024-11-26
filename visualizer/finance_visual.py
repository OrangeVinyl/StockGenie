import os
import pandas as pd
import mplfinance as mpf
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, timedelta

def get_stock_csv_path(company_name):
    """
    @description 지정된 회사 이름에 해당하는 CSV 파일의 경로를 반환하는 함수

    :param company_name:
    :return stock_csv_data: str
    """
    csv_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    stock_csv_folder_path = os.path.join(csv_dir, 'data', 'stocks')
    stock_csv_data = os.path.join(stock_csv_folder_path, f"{company_name}_stock_dataset.csv")
    return stock_csv_data


def load_stock_data(company_name):
    """
    @description 지정된 회사의 CSV 파일을 읽어 DataFrame으로 반환하는 함수

    :param company_name:
    :return stock_df: pd.DataFrame
    """
    stock_csv_data = get_stock_csv_path(company_name)
    stock_df = pd.read_csv(stock_csv_data, parse_dates=['Date'])
    return stock_df


def visualize_finance(company_name):
    """
    @description Pandas의 기본 플롯을 사용한 종가 추이 시각화 함수

    :param company_name:
    :return fig: plt.Figure
    """
    stock_df = load_stock_data(company_name)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(stock_df['Date'], stock_df['Close'], label='Close')
    ax.set_title(f"{company_name} Close Price")
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid(True)

    return fig


def visualize_finance_interactive_line(company_name):
    """
    @description Plotly를 사용한 인터랙티브 종가 추이 시각화 함수

    :param company_name:
    :return fig: go.Figure
    """
    stock_df = load_stock_data(company_name)
    fig = px.line(stock_df, x='Date', y='Close', title=f"{company_name} Close Price")
    fig.update_layout(xaxis_title='Date', yaxis_title='Price')

    return fig


def visualize_finance_interactive_candlestick(company_name):
    """
    @description Plotly를 사용한 인터랙티브 캔들스틱 차트 시각화 함수

    :param company_name:
    :return fig: go.Figure
    """
    stock_df = load_stock_data(company_name)
    fig = go.Figure(data=[go.Candlestick(
        x=stock_df['Date'],
        open=stock_df['Open'],
        high=stock_df['High'],
        low=stock_df['Low'],
        close=stock_df['Close'],
        name='Candlestick'
    )])

    fig.update_layout(
        title="Candlestick Chart - (Interactive)",
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False
    )

    return fig


def visualize_finance_mplfinance(company_name):
    """
    @description mplfinance를 사용하여 한 달치 주가 추이 및 캔들스틱 차트를 시각화하는 함수

    :param company_name:
    :return fig: plt.Figure
    """
    stock_df = load_stock_data(company_name)

    one_month_ago = pd.Timestamp(datetime.today() - timedelta(days=30)).tz_localize(stock_df['Date'].dt.tz)
    one_month_df = stock_df[stock_df['Date'] >= one_month_ago]
    one_month_df.set_index('Date', inplace=True)

    mc = mpf.make_marketcolors(
        up='r',
        down='b',
        inherit=True
    )
    s = mpf.make_mpf_style(marketcolors=mc)

    fig, axlist = mpf.plot(one_month_df, type='candle', style=s,
                           title="Monthly Candlestick Chart",
                           ylabel='price',
                           volume=True,
                           mav=(3, 6, 9),
                           returnfig=True)
    return fig

def run_finance_visual(company_name):
    fig1 = visualize_finance(company_name)
    fig2 = visualize_finance_mplfinance(company_name)
    fig3 = visualize_finance_interactive_line(company_name)
    fig4 = visualize_finance_interactive_candlestick(company_name)

    return fig1, fig2, fig3, fig4

def test_finance_visual():
    company_name = '한화오션'

    visualize_finance(company_name)
    visualize_finance_mplfinance(company_name)
    visualize_finance_interactive_line(company_name)
    visualize_finance_interactive_candlestick(company_name)
