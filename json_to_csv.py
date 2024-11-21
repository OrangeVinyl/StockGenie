import json
import pandas as pd
import os
import re

def extract_data_from_json(json_file_path):
    """
    JSON 파일에서 필요한 데이터를 추출하는 함수.
    필요한 필드: title, summary, publish_date, positive, neutral, negative
    """
    with open(json_file_path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 에러: {json_file_path} - {e}")
            return []
        except Exception as e:
            print(f"파일 읽기 에러: {json_file_path} - {e}")
            return []

    # JSON 데이터가 리스트 형태인지 확인
    if isinstance(data, dict):
        # 데이터가 딕셔너리라면, 리스트로 감싸기
        articles = [data]
    elif isinstance(data, list):
        articles = data
    else:
        print(f"예상하지 못한 JSON 형식: {json_file_path}")
        return []

    extracted = []
    for article in articles:

        title = article.get('title', '')
        summary = article.get('summary', '')
        publish_date = article.get('publish_date', '')

        # aggregate_scores에서 감성 점수 추출
        aggregate_scores = article.get('aggregate_scores', {})
        positive = aggregate_scores.get('positive', 0.0)
        neutral = aggregate_scores.get('neutral', 0.0)
        negative = aggregate_scores.get('negative', 0.0)

        extracted.append({
            'title': title,
            'summary': summary,
            'publish_date': publish_date,
            'positive': positive,
            'neutral': neutral,
            'negative': negative
        })
    return extracted


def run(company_name, source):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    json_folder_path = os.path.join(script_dir, 'data', 'processed_articles')
    csv_folder_path = os.path.join(script_dir, 'data', 'csv_datasets')

    if not os.path.exists(csv_folder_path):
        os.makedirs(csv_folder_path)

    all_extracted_data = []

    if source == 'naver':
        json_filename = f"{company_name}_naver_summarized_articles.json"
    elif source == 'news':
        json_filename = f"{company_name}_news_summarized_articles.json"

    file_path = os.path.join(json_folder_path, f"{company_name}_{source}_summarized_articles.json")
    extracted = extract_data_from_json(file_path)

    if extracted:
        all_extracted_data.extend(extracted)

    df = pd.DataFrame(all_extracted_data)
    df['publish_date'] = pd.to_datetime(df['publish_date'], errors='coerce')
    df['publish_date'] = df['publish_date'].dt.strftime('%Y-%m-%d')

    df['title'] = df['title'].fillna('')
    df['summary'] = df['summary'].fillna('')
    df['publish_date'] = df['publish_date'].fillna(pd.Timestamp('1970-01-01'))
    df['positive'] = df['positive'].fillna(0.0)
    df['neutral'] = df['neutral'].fillna(0.0)
    df['negative'] = df['negative'].fillna(0.0)

    # CSV 파일로 저장
    csv_filename = f"{company_name}_datasets.csv"
    csv_file_path = os.path.join(csv_folder_path, csv_filename)
    df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

    print(f"선택된 JSON 파일이 성공적으로 CSV로 변환되었습니다: {csv_file_path}")


def test_json_to_csv():
    run('Intel', 'news')


