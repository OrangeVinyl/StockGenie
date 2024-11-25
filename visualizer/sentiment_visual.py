import os
import pandas as pd
from matplotlib import rc
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import matplotlib.font_manager as fm

from util.check_platform import get_os

font_path = None
if get_os() == 'Windows':
    font_path = 'C:/Windows/Fonts/NanumGothic.ttf'
    font_name = fm.FontProperties(fname=font_path).get_name()
    plt.rc('font', family=font_name)
elif get_os() == 'macOS':
    font_path = '/Library/Fonts/Supplemental/AppleGothic.ttf'
    rc('font', family='AppleGothic')
    plt.rcParams['axes.unicode_minus'] = False



def load_data(company_name):
    script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    csv_folder_path = os.path.join(script_dir, 'data', 'csv_datasets')

    full_csv_data = os.path.join(csv_folder_path, f"{company_name}_datasets.csv")
    aggregated_csv_data = os.path.join(csv_folder_path, f"{company_name}_aggregated.csv")


    full_df = pd.read_csv(full_csv_data)
    aggregated_df = pd.read_csv(aggregated_csv_data)


    return full_df, aggregated_df

def daily_sentiment_visualize(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['publish_date'], y=df['positive'],
        mode='lines+markers', name='Positive',
        line=dict(color='green', width=3), marker=dict(size=8)
    ))

    fig.add_trace(go.Scatter(
        x=df['publish_date'], y=df['neutral'],
        mode='lines+markers', name='Neutral',
        line=dict(color='blue', width=3, dash='dash'), marker=dict(size=8)
    ))

    fig.add_trace(go.Scatter(
        x=df['publish_date'], y=df['negative'],
        mode='lines+markers', name='Negative',
        line=dict(color='red', width=3, dash='dot'), marker=dict(size=8)
    ))

    fig.update_layout(
        title='Daily Sentiment Distribution',
        xaxis_title='publish_date',
        yaxis_title='Proportion',
        legend_title='Sentiment',
        template='plotly_white',
        font=dict(size=14),
        xaxis=dict(showgrid=True, gridcolor='LightGray'),
        yaxis=dict(showgrid=True, gridcolor='LightGray'),
        legend=dict(bordercolor='Black', borderwidth=1)
    )

    fig.show()

def main_sentiment_visualize(df):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['publish_date'],
        y=df['negative'],
        name='Negative',
        marker_color='#d62728'
    ))
    fig.add_trace(go.Bar(
        x=df['publish_date'],
        y=df['neutral'],
        name='Neutral',
        marker_color='#1f77b4'
    ))
    fig.add_trace(go.Bar(
        x=df['publish_date'],
        y=df['positive'],
        name='Positive',
        marker_color='#2ca02c'
    ))
    fig.update_layout(
        barmode='stack',
        title='Stacked Bar Chart of Sentiment Proportions',
        xaxis=dict(title='publish_date', tickformat='%Y-%m-%d', tickangle=45),
        yaxis=dict(title='Proportion'),
        legend_title='Sentiment',
        template='plotly_white'
    )

    fig.show()

def word_cloud_visualize(df):
    summaries = df['summary']

    all_text = ' '.join(summaries)
    words = all_text.split()

    ## TODO: 형태소 분석

    word_counts = Counter(words)    # 단어 빈도수 계산
    most_common_words = word_counts.most_common(20)    # 가장 많이 사용된 20개의 단어 추출

    # 가장 많이 사용된 단어들의 막대 차트 생성
    words, counts = zip(*most_common_words)
    plt.figure(figsize=(10, 6))
    plt.bar(words, counts)
    plt.title('Top 20 Most Common Words in Summaries')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font_path).generate_from_frequencies(word_counts)
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Summaries')
    plt.show()


def test_sentiment_visual():
    full_df, aggregated_df = load_data('삼성전자')
    daily_sentiment_visualize(aggregated_df)
    main_sentiment_visualize(aggregated_df)
    word_cloud_visualize(full_df)
    print(aggregated_df.head())
