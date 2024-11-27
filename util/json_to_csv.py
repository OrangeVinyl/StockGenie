import os
import json
import pandas as pd

def extract_data_from_json(json_file_path):
    """
    @description JSON 파일에서 필요한 데이터를 추출하는 함수

    :param json_file_path: JSON 파일 경로
    """
    with open(json_file_path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"[ERROR] extract_data_from_json: {json_file_path} - {e}")
            return []
        except Exception as e:
            print(f"[ERROR] 파일 읽기 에러: {json_file_path} - {e}")
            return []

    if isinstance(data, dict):
        articles = [data]
    elif isinstance(data, list):
        articles = data
    else:
        print(f"[ERROR] 예상하지 못한 JSON 형식: {json_file_path}")
        return []

    extracted = []
    for article in articles:
        if 'content' != '':
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


def save_raw_data(df, csv_folder_path, company_name):
    """
    @description 정제된 데이터를 원본 CSV 파일로 저장하는 함수

    :param df: 정제된 데이터프레임
    :param csv_folder_path: CSV 파일들이 저장될 폴더 경로
    :param company_name: 기업명
    """
    csv_filename = f"{company_name}_datasets.csv"
    csv_file_path = os.path.join(csv_folder_path, csv_filename)

    df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
    print(f"\n[SUCCESS] save_raw_data: {csv_file_path}")


def aggregate_and_save(df, csv_folder_path, company_name):
    """
    @description 날짜별로 데이터를 집계하고 평균을 계산하여 별도의 CSV 파일로 저장하는 함수

    :param df: 정제된 데이터프레임
    :param csv_folder_path: CSV 파일들이 저장될 폴더 경로
    :param company_name: 기업명
    """
    grouped = df.groupby('publish_date').agg({
        'positive': 'mean',
        'neutral': 'mean',
        'negative': 'mean'
    }).reset_index()

    def determine_total(row):
        sentiments = {'positive': row['positive'], 'neutral': row['neutral'], 'negative': row['negative']}
        return max(sentiments, key=sentiments.get)

    grouped['total'] = grouped.apply(determine_total, axis=1)

    aggregated_csv_filename = f"{company_name}_aggregated.csv"
    aggregated_csv_file_path = os.path.join(csv_folder_path, aggregated_csv_filename)
    grouped.to_csv(aggregated_csv_file_path, index=False, encoding='utf-8-sig')

    print(f"[SUCCESS] aggregate_and_save: {aggregated_csv_file_path}")

def run(company_name, source):
    """
    @description JSON 파일을 CSV 파일로 변환하는 함수

    :param company_name: 기업 이름
    :param source: news | naver
    """
    script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    json_folder_path = os.path.join(script_dir, 'data', 'processed_articles')
    csv_folder_path = os.path.join(script_dir, 'data', 'csv_datasets')

    if not os.path.exists(csv_folder_path):
        os.makedirs(csv_folder_path)

    all_extracted_data = []

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

    save_raw_data(df, csv_folder_path, company_name)
    aggregate_and_save(df, csv_folder_path, company_name)

def test_json_to_csv():
    run('한화오션', 'naver')


