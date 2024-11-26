import os
import pandas as pd
import xgboost as xgb
from datetime import timedelta
import matplotlib.pyplot as plt

"""
@title: predict_model_script.py
@description: 주가 예측 모델을 활용하여 다음 날 주가를 예측하고 시각화하는 스크립트

- 데이터 로드
- 감성 데이터 병합
- 감성 데이터 결측치 처리
- 주가데이터 병합
- Feature 설정
- DMatrix 변환
- 다음 날 종가 예측
- 다음 날 주가 데이터를 예측 결과로 생성
- 데이터 시각화

:param company_name: str - 기업명
:param soruce: str - ('국내', '해외')
"""

def run_predict_model(company_name, source):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'csv_datasets'))
    data_csv = os.path.join(base_dir, f"{company_name}_aggregated.csv")
    stock_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'stocks'))
    stock_csv = os.path.join(stock_base_dir, f"{company_name}_stock_dataset.csv")

    new_sentiment_df = pd.read_csv(data_csv)
    new_stock_df = pd.read_csv(stock_csv)

    # 날짜 형식 변환 (UTC 설정 추가)
    new_sentiment_df['publish_date'] = pd.to_datetime(new_sentiment_df['publish_date'], utc=True)
    new_stock_df['Date'] = pd.to_datetime(new_stock_df['Date'], utc=True)

    # 날짜 형식을 date만 남기도록 설정
    new_sentiment_df['Date'] = new_sentiment_df['publish_date'].dt.date
    new_stock_df['Date'] = new_stock_df['Date'].dt.date

    # 감성 데이터 병합 (기준: new_stock_df)
    new_data = pd.merge(new_stock_df, new_sentiment_df, on='Date', how='left')

    # 감성 데이터 결측치 처리
    new_data['positive'] = new_data['positive'].fillna(0)
    new_data['negative'] = new_data['negative'].fillna(0)

    new_data['sentiment_score'] = new_data['positive'] - new_data['negative']
    new_data['sentiment_score'] = new_data['sentiment_score'] * (1 - new_data['neutral'])

    # 필요 없는 열 제거
    new_data.drop(['Dividends', 'Stock Splits', 'total'], axis=1, errors='ignore', inplace=True)

    # 가장 최신 날짜 확인
    last_available_date = new_data['Date'].max()
    print(f"Last available market date: {last_available_date}")

    # 최근 7일간의 주가 데이터 가져오기
    recent_7_days_data = new_data[new_data['Date'] > last_available_date - timedelta(days=7)]
    print(f"Recent 7 days data\n{recent_7_days_data[['Date', 'Close']]}")

    # 다음 예측 날짜 계산
    if last_available_date.weekday() == 4: # 금요일
        predict_date = last_available_date + timedelta(days=3) # 월요일
    else:
        predict_date = last_available_date + timedelta(days=1)

    print(f"Next prediction date: {predict_date}")

    # 특징 설정
    features = ['Open', 'High', 'Low', 'Close', 'Volume', 'sentiment_score']
    X_predict = new_data[new_data['Date'] == last_available_date][features]

    if X_predict.empty:
        print(f"No data available for the date: {last_available_date}")
    else:
        d_predict = xgb.DMatrix(X_predict, feature_names=features)
        predict_model = xgb.Booster()
        model_path = ''

        if source == '해외':
            model_path = os.path.join(os.path.dirname(__file__), 'kor_pr_model_up.json')
        elif source == '국내':
            model_path = os.path.join(os.path.dirname(__file__), 'kor_pr_model_up.json')

        predict_model.load_model(model_path)

        # 다음 날 종가 예측
        predicted_price = predict_model.predict(d_predict)

        # 다음 날 주가 데이터를 예측 결과로 생성
        future_data = pd.DataFrame({
            'Date': [predict_date],
            'Close': [predicted_price[0]]
        })

        print(f"Next prediction Close : {predicted_price[0]}")

        # 최근 7일 데이터에 예측 데이터 추가
        combined_data = pd.concat([recent_7_days_data[['Date', 'Close']], future_data], ignore_index=True)

        # 시각화 - 실제 주가와 예측된 주가
        plt.figure(figsize=(12, 6))

        # 최근 7일간의 실제 주가
        plt.plot(combined_data['Date'][:-1], combined_data['Close'][:-1], label='Actual Close Price (Last 7 Days)', color='blue', marker='o', linestyle='-', alpha=0.7)

        # 예측된 다음 날 주가
        plt.plot(combined_data['Date'][-2:], combined_data['Close'][-2:], label='Predicted Next Day Close Price', color='red', linestyle='--', marker='x', markersize=10)

        # 그래프 장식
        plt.title('Stock Price: Last 7 Days and Predicted Next Day')
        plt.xlabel('Date')
        plt.ylabel('Stock Price')
        plt.xticks(rotation=45)
        plt.grid(visible=True)
        plt.legend()
        plt.tight_layout()

        # 그래프 표시
        plt.show()


def test_predict_model():
    run_predict_model('한화오션', '국내')