import os
import json
import requests
import datetime
from newspaper import Article
from dotenv import load_dotenv
from trafilatura import fetch_url, extract
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

limit_days = 7

def get_news_search(api_key, query, from_date, to_date, page=1, page_size=100):
    """
    @description: 뉴스 검색 API를 이용하여 뉴스를 검색하는 함수

    :param api_key:
    :param query:
    :param from_date:
    :param to_date:
    :param page: int - 페이지 번호(default: 1)
    :param page_size: int - 한 페이지에 출력할 결과 수(max: 100)
    :return: data | None - API 응답 데이터
    """
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': query,
        'from': from_date,
        'to': to_date,
        'language': 'en',
        'page': page,
        'pageSize': page_size,
        'sortBy': 'publishedAt',
        'apiKey': api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get('status') != 'ok':
            print(f"[ERROR] News API ERROR: {data.get('message')}")
            return None

        return data

    except requests.exceptions.HTTPError as http_err:
        print(f"[ERROR] HTTP ERROR: {http_err}")

    except Exception as e:
        print(f"[ERROR] News API request ERROR: {e}")

    return None

def parse_article(url, language='en'):
    """
    @description: 주어진 URL의 기사를 파싱하여 본문을 추출하는 함수
    - newspaper3k를 이용하여 본문 추출 시도
    - 실패할 경우 trafilatura를 이용하여 본문 추출 시도

    :param url:
    :param language: str - 언어(default: en)
    :return: text | None
    """
    try:
        article = Article(url, language=language)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"[INFO] Failed newspaper3k ({url}): {e}")

    try:
        downloaded = fetch_url(url)
        if downloaded is None:
            print(f"[ERROR] Failed to fetch URL with trafilatura: {url}")
            return None
        text = extract(downloaded, include_comments=False, include_tables=False)
        return text
    except Exception as e:
        print(f"[INFO] Failed trafilatura ({url}): {e}")
        return None

def filter_article(article, query, cutoff_date):
    """
    @description: 기사를 필터링하는 함수

    :param article:
    :param query:
    :param cutoff_date:
    :return: bool
    """
    title = (article.get('title') or '').lower()
    description = (article.get('description') or '').lower()
    published_at = article.get('publishedAt', '') or ''

    pub_date = datetime.datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
    query_words = query.lower().split()

    if any(word in title or word in description for word in query_words) and pub_date >= cutoff_date:
        return True

    return False

def save_to_json(data, company_name):
    """
    @description: JSON 파일로 저장하는 함수

    :param data:
    :param company_name:
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_dir = os.path.join(base_dir, 'data', 'news_articles')

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    save_path = os.path.join(save_dir, f'{company_name}_news_articles.json')

    with open(save_path, 'w', encoding='utf8') as outfile:
        res = json.dumps(data, indent=4, sort_keys=False, ensure_ascii=False)
        outfile.write(res)

    print('[SUCCESS] %s_news_articles.json SAVED' % company_name)
    print(f'[SUCCESS] {save_path} SAVED')

def run(company_name):
    today = datetime.datetime.now()
    days_ago = today - datetime.timedelta(days=limit_days)
    json_result = []

    cnt = 1
    total_results = 0
    min_articles = 20  # 최소 기사 수
    max_articles = 210  # 최대 기사 수

    dates_with_articles = set()
    date_range = {(days_ago + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(limit_days)}

    for i in range(limit_days):
        single_day = (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        print(f"================= {single_day} =================")

        data = get_news_search(API_KEY, company_name, single_day, single_day, page=1, page_size=100)
        if data:
            articles = data.get('articles', [])
            total_results += data.get('totalResults', 0)

            if not articles:
                print(f"[WARN] {single_day}에 대한 기사가 없습니다.")
                continue

            filtered_articles = [article for article in articles if filter_article(article, company_name, days_ago)]
            if not filtered_articles:
                print(f"[WARN] {single_day}에 필터링된 기사가 없습니다.")
                continue

            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_article = {executor.submit(parse_article, article['url']): article for article in filtered_articles}

                for future in as_completed(future_to_article):
                    article = future_to_article[future]
                    try:
                        content = future.result()

                        if content:
                            pub_date_str = article.get('publishedAt', '')
                            publish_date = datetime.datetime.strptime(pub_date_str, '%Y-%m-%dT%H:%M:%SZ')
                            dates_with_articles.add(publish_date.strftime('%Y-%m-%d'))

                            json_result.append({
                                'cnt': cnt,
                                'title': article.get('title', ''),
                                'description': article.get('description', ''),
                                'link': article.get('url', ''),
                                'publish_date': article.get('publishedAt', ''),
                                'content': content
                            })

                            cnt += 1
                            if len(json_result) >= max_articles:
                                break

                    except Exception as e:
                        print(f"[ERROR] 본문 추출 실패 ({article.get('url', '')}): {e}")

            if len(json_result) >= max_articles:
                break

    save_to_json(json_result, company_name)

    if len(json_result) >= min_articles and date_range.issubset(dates_with_articles):
        print("[INFO] 조건 충족: 최소 20개의 기사와 각 날짜별로 최소 1개의 기사 수집 완료.")

    print("\n===== [검색 결과] =====")
    print(f"[INFO] 전체 검색 결과: {total_results} 건")
    print(f"[INFO] 수집된 데이터: {len(json_result)} 건\n")


def test_news_crawl():
    run('nvidia')