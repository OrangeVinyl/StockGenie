# StockGeine

### 생성형AI를 활용한 주식 예측 프로그램 개발

---
## ✅ 개요

---
### 1. 프로젝트 목표

가) 특정 기업의 최근 금융 뉴스를 수집 

나) 수집된 뉴스의 감성 분석 수행

다) 감성 분석 결과와 해당 기업의 주가 변동 간의 상관관계 분석

라) 간단한 주가 동향 예측 모델 구현 

마) 결과를 시각화하여 사용자에게 제공

### 2. 세부 단계 및 목표

**가) 데이터 수집**

목표: 입력된 기업에 대해 `최소 20개`의 최근 뉴스 기사와 해당 기간의 `일별` 주가 데이터 수집

- 사용자로부터 `기업명 입력 받기` (국내/국외 선택, 둘다 가능)
- 입력된 기업에 대한 최근 뉴스 기사 수집 (예: 최근 1주일)
- 생성형 AI를 활용한 뉴스 기사 요약
    - `Open AI API` 활용
- 뉴스 API 사용 (예: Naver API, NewsAPI, Google News API 등등)
- 해당 기업의 주가 데이터 수집
- 금융 데이터 API 사용 (예: Yahoo Finance APl, Alpha Vantage)

**나) 텍스트 전처리 및 감성분석**

목표: 각 뉴스 기사에 대해 긍정/부정/중립 점수 산출

- 수집된 뉴스 기사 텍스트 전처리
- 불필요한 문자 제거, 소문자 변환 등
- 불필요한 문자 제거, 소문자 변환 등
- 감성분석 진행 (예: NLTK, TextBlob 라이브러리 사용)
    - 사용하는 이유 - 판단하는 이유?
    - 머신러닝으로 학습하는거랑 비교
    - 감성어분석으로 하는거랑 비교

**다) 데이터 분석 및 시각화**

목표: 뉴스 감성과 주가 변동의 관계를 보여주는 그래프 생성

- 일별 뉴스 감성 점수 평균 계산
- 주가 변동과 뉴스 감성 점수 간의 상관관계 분석
- 결과 시각화 (예: matplotlib 또는 plotly 사용)

**라) 예측 모델 구현**

목표: 뉴스 감성을 바탕으로 다음 날의 주가 방향(상승/하락) 예측

- 뉴스 감성 점수를 입력으로 사용하는 예측 모델 구현 (예: scikit-learn 라이브러리 사용)
- 주가, 거래량 등의 정형 데이터와 감성 정보를 결합하여 자유롭게 예측 모델을 구현
- 모델 학습 및 평가

**마) 사용자 인터페이스 및 최종 정리**

목표: 사용자 기업명 입력하면 전체 분석 과정이 자동 실행되고 결과가 출력되는 시스템 완성

- 간단한 커맨드 라인 인터페이스 구현 (예: 웹, 커맨드 등)
- 사용자 입력에 따른 전체 프로세스 `자동화`
- `결과 보고서 생성 기능 추가` (예: 웹, PDF 등)
- `예측 결과 및 기업 뉴스 및 동향 요약자료`, `주가 변동 그래프` 등

### 3. 최종 산출물

**가) 파이썬 스크립트: 전체 프로세스를 포함한 실행 가능한 코드** 

**나) 간단한 사용자 가이드: 프로그램 사용 방법 설명** 

**다) 샘플 결과 보고서: 특정 기업에 대한 분석 결과 예시**

**라) 과제 발표**

## 🔗 Requirements

---
**개발 환경**

- Python ~== `3.9.13`
- `virtualenv`

**가상환경 구동**

- Window
    
    ```
    > source .venv/Scripts/activate 
    ```
    
- MacOs
    
    ```
    > source .venv/bin/activate
    ```
    

**ENV(Keys)**

```
## Naver API
NAVER_CLIENT=
NAVER_SECRET=

## Google API
GOOGLE_API_KEY=

## OpenAI API
OPENAI_API_KEY=

## LangSmith API
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=StockGenie

## News API
NEWS_API_KEY=
```

**의존성 및 라이브러리 설치**

```
> pip install -r requirements.txt
```
**애플리케이션 구동**

```
> streamlit run app.py
```

## 📦 Directory

---

```angular2html
📦 StockGeine
├─.gitignore
├─ README.md
├─ app.py
├─ crawlers
│  ├─ __init__.py
│  ├─ naver_crawl.py
│  ├─ news_crawl.py
├─ data
│  ├─ csv_datasets
│  ├─ naver_article
│  ├─ news_article
│  ├─ plot
│  ├─ processed_article
│  ├─ stock
│  ├─ mapped_emotion_dataset.csv
│  └─ stopwords.txt
├─ finance
│  ├─ __init__.py
│  ├─ finance_reader.py
│  ├─ stock_ticker.py
│  └─ yfinance_reader.py
├─ logs
├─ main.py
├─ model
│  ├─ __init__.py
│  ├─ en_predict_model.json
│  ├─ predict_model_script.py
│  ├─ kor_predict_model.jso
│  ├─ make_predict_model.ipynb
│  └─ train_more_data_and_run.ipyn
├─ preprocessing
│  ├─ __init__.py
│  ├─ cleaner.py
│  ├─ morphological.py
│  ├─ spacing.py
│  └─ splitter.py
├─ requirements.txt
├─ sentiment
│  ├─ __init__.py
│  ├─ en_sentiment.py
│  └─ ko_sentiment.py
├─ summarizer
│  ├─ __init__.py
│  └─ prompts.py
├─ util
│  ├─ __init__.py
│  ├─ check_platform.py
│  ├─ json_to_csv.py
│  ├─ label_filter.py
│  ├─ logger.py
│  └─ pre_train_model.py
└─ visualize
   ├─ __init__.py
   ├─ finance_visual.py
   └─ sentiment_visual.py

```
