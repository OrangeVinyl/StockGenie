import os
import pandas as pd
from . import font_path
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from preprocessing.morphological import extract_relevant_words_ko, extract_relevant_words_en

def load_data(company_name):
    """
    @description 데이터를 로드하는 함수

    :param company_name:
    :return full_df, aggregated_df: pd.DataFrame, pd.DataFrame
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'csv_datasets'))
    full_csv = os.path.join(base_dir, f"{company_name}_datasets.csv")
    aggregated_csv = os.path.join(base_dir, f"{company_name}_aggregated.csv")

    try:
        full_df = pd.read_csv(full_csv)
        aggregated_df = pd.read_csv(aggregated_csv)
    except FileNotFoundError as e:
        print(f"데이터 파일을 찾을 수 없습니다: {e}")
        raise

    return full_df, aggregated_df


def daily_sentiment_visualize(df):
    """
    @description 일별 감성 분포를 시각화하는 함수
    - Plotly를 사용한 인터랙티브한 선 그래프

    :param df: 'publish_date', 'positive', 'neutral', 'negative' 컬럼을 포함한 데이터프레임
    :return fig: go.Figure
    """
    fig = go.Figure()

    sentiment_styles = {
        'positive': {'color': 'green', 'dash': 'solid'},
        'neutral': {'color': 'blue', 'dash': 'dash'},
        'negative': {'color': 'red', 'dash': 'dot'}
    }

    for sentiment, style in sentiment_styles.items():
        fig.add_trace(go.Scatter(
            x=df['publish_date'],
            y=df[sentiment],
            mode='lines+markers',
            name=sentiment.capitalize(),
            line=dict(color=style['color'], width=3, dash=style['dash']),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title='Daily Sentiment Distribution',
        xaxis_title='Publish Date',
        yaxis_title='Proportion',
        legend_title='Sentiment',
        template='plotly_white',
        font=dict(size=14),
        xaxis=dict(showgrid=True, gridcolor='LightGray'),
        yaxis=dict(showgrid=True, gridcolor='LightGray'),
        legend=dict(bordercolor='Black', borderwidth=1)
    )

    return fig

def main_sentiment_visualize(df):
    """
    @description 주요 감성 분포를 시각화하는 함수
    - Plotly를 사용한 스택형 막대 그래프

    :param df: 'publish_date', 'positive', 'neutral', 'negative' 컬럼을 포함한 데이터프레임
    :return fig: go.Figure
    """
    fig = go.Figure()

    sentiment_colors = {
        'negative': '#d62728',
        'neutral': '#1f77b4',
        'positive': '#2ca02c'
    }

    for sentiment in ['negative', 'neutral', 'positive']:
        fig.add_trace(go.Bar(
            x=df['publish_date'],
            y=df[sentiment],
            name=sentiment.capitalize(),
            marker_color=sentiment_colors[sentiment]
        ))

    fig.update_layout(
        barmode='stack',
        title='Stacked Bar Chart of Sentiment Proportions',
        xaxis=dict(title='Publish Date', tickformat='%Y-%m-%d', tickangle=45),
        yaxis=dict(title='Proportion'),
        legend_title='Sentiment',
        template='plotly_white'
    )

    return fig


def word_cloud_visualize(df, source):
    """
    @description 요약 내용의 단어 빈도수를 기반으로 시각화하는 함수
    - 막대 그래프와 워드 클라우드를 활용

    :param df: 전체 데이터프레임
    :param source: str - '국내' 또는 '해외'
    """
    summaries = df['summary'].dropna().astype(str)

    all_words = []
    for text in summaries:
        if source == '국내':
            words = extract_relevant_words_ko(text)
        elif source == '해외':
            words = extract_relevant_words_en(text)
        all_words.extend(words)

    # 단어 빈도수 계산
    word_counts = Counter(all_words)
    most_common_words = word_counts.most_common(20)

    ## 상위 20개 단워 막대 그래프 생성
    words, counts = zip(*most_common_words) if most_common_words else ([], [])
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(words, counts, color='skyblue')
    ax.set_title('Top 20 Most Common Words in Summaries')
    ax.set_ylabel('Frequency')
    ax.set_xticklabels(words, rotation=45, ha='right')
    plt.tight_layout()


    if font_path and os.path.exists(font_path):
        wc = WordCloud(width=800, height=400, background_color='white', font_path=font_path)
    else:
        wc = WordCloud(width=800, height=400, background_color='white')
        print("경고: 지정된 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")

    wordcloud = wc.generate_from_frequencies(word_counts)

    fig_wc, ax_wc = plt.subplots(figsize=(10, 6))
    ax_wc.imshow(wordcloud, interpolation='bilinear')
    ax_wc.axis('off')
    ax_wc.set_title('Word Cloud of Summaries')

    fig.show()
    fig_wc.show()

    return fig, fig_wc

def run_sentiment_visual(company_name, source):
    try:
        full_df, aggregated_df = load_data(company_name)
    except FileNotFoundError:
        print("데이터 로드에 실패했습니다.")
        return

    fig1 = daily_sentiment_visualize(aggregated_df)
    fig2 = main_sentiment_visualize(aggregated_df)
    fig3, fig4 = word_cloud_visualize(full_df, source)

    return fig1, fig2, fig3, fig4

def test_sentiment_visual():
    company_name = '한화오션'
    source = '국내'

    try:
        full_df, aggregated_df = load_data(company_name)
    except FileNotFoundError:
        print("데이터 로드에 실패했습니다.")
        return

    fig1 = daily_sentiment_visualize(aggregated_df)
    fig2 = main_sentiment_visualize(aggregated_df)
    fig3, fig4 = word_cloud_visualize(full_df, source)

    print(aggregated_df.head())