import os
import logging
import requests
import datetime
import json
from newspaper import Article
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

def fetch_news(api_key, query, from_date, to_date, page, language='en'):
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': query,
        'from': from_date,
        'to': to_date,
        'language': language,
        'page': page,
        'sortBy': 'publishedAt',
        'apiKey': api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get('status') != 'ok':
            logging.error(f"[ERROR] News API ERROR: {data.get('message')}")
            return None

        return data

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"[ERROR] HTTP error: {http_err}")

    except Exception as e:
        logging.error(f"[ERROR] News API request failure: {e}")

        return None


def parse_article(url, language='en'):
    try:
        article = Article(url, language=language)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        logging.error(f"[ERROR] Parsing Failure ({url}): {e}")
        return None


def filter_article(article, query, cutoff_date):
    if not article:
        logging.warning("[WARN] 받은 데이터가 없습니다.")
        return False

    print(article)

    title = (article.get('title') or '').lower()
    description = (article.get('description') or '').lower()
    published_at = article.get('publishedAt', '') or ''

    try:
        pub_date = datetime.datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        logging.warning(f"[WARN] 잘못된 날짜 형식 : {published_at}")
        return False

    query_words = query.lower().split()
    if any(word in title or word in description for word in query_words) and pub_date >= cutoff_date:
        return True
    return False


def save_to_json(data, company_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_dir = os.path.join(base_dir, 'data', 'news_articles')

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    filename = f"{company_name}_news_articles.json"
    save_path = os.path.join(save_dir, filename)


    with open(save_path, 'w', encoding='utf8') as outfile:
        res = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(res)

    print('[SUCCESS] %s_news_articles.json SAVED' % company_name)
    print(f'[SUCCESS] {save_path} SAVED')


def run(company_name):

    today = datetime.datetime.utcnow()
    seven_days_ago = today - datetime.timedelta(days=7)

    from_date = seven_days_ago.strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    all_articles = []
    page = 1
    total_results = None
    json_result = []
    cnt = 0

    dates_with_articles = set()
    date_range = [(seven_days_ago + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

    page_size = 100  # 페이지당 기사 수
    max_pages = 100  # News API의 최대 페이지 수

    while page <= max_pages:
        print(f"================= {max_pages} =========================")
        print(f"================= {page} 페이지 =================")
        data = fetch_news(API_KEY, company_name, from_date, to_date, page=page)
        if data:
            articles = data.get('articles', [])
            if total_results is None:
                total_results = data.get('totalResults', 0)
                # 실제로 가져올 수 있는 최대 페이지 수 계산
                max_pages = min((total_results + page_size - 1) // page_size, 100)

            if not articles:
                print("[WARN] 더 이상 가져올 기사가 없습니다.")
                break
            total_results = data.get('totalResults')
            print(f"------------------------  {total_results}")
            for article in articles:
                if filter_article(article, company_name, seven_days_ago):
                    all_articles.append(article)

                    # 날짜를 추출하여 dates_with_articles에 추가
                    published_at = article.get('publishedAt', '')
                    try:
                        pub_date = datetime.datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
                        dates_with_articles.add(pub_date.strftime('%Y-%m-%d'))
                    except ValueError:
                        print(f"[WARN] 잘못된 날짜 형식: {published_at}")

                    # 충분한 기사와 날짜가 확보되었는지 확인
                    if len(all_articles) >= 100:
                        break

            print(f"[SUCCESS] 페이지 {page}: {len(articles)}개 기사 중 {len(all_articles)}개 수집됨.")

            # 조건이 충족되었는지 확인
            if len(all_articles) >= 20 and all(date in dates_with_articles for date in date_range):
                print("[INFO] 조건 충족: 최소 20개의 기사와 각 날짜별로 최소 1개의 기사 수집 완료.")
                break

            # 최대 기사 수집량에 도달했는지 확인
            if len(all_articles) >= 100:
                print("[INFO] 최대 기사 수집량(100개)에 도달했습니다.")
                break

            # 페이지 증가
            page += 1
        else:
            print("[INFO] 데이터를 가져오지 못했습니다.")
            break

    # 모든 페이지를 순회한 후에도 조건이 충족되지 않았을 경우
    if len(all_articles) < 20 or not all(date in dates_with_articles for date in date_range):
        print("[WARN] 모든 페이지를 가져왔지만 조건을 충족하지 못했습니다.")
        print("[INFO] 검색 기간을 늘리거나 검색어를 변경해보세요.")

    print(f"[INFO] 총 {len(all_articles)}개의 기사를 수집했습니다.")

    ## 멀티 스레딩
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_article = {executor.submit(parse_article, article['url']): article for article in all_articles}
        for future in as_completed(future_to_article):
            article = future_to_article[future]
            try:
                content = future.result()
                if content:
                    cnt += 1
                    json_result.append({
                        'cnt': cnt,
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'link': article.get('url', ''),
                        'publish_date': article.get('publishedAt', ''),
                        'content': content
                    })
            except Exception as e:
                print(f"[ERROR] ThreadPoolExecutor - ({article.get('url', '')}): {e}")

    # # 멀티스레딩 없이 기사 처리
    # for article in all_articles:
    #     try:
    #         content = parse_article(article['url'])
    #         if content:
    #             cnt += 1
    #             json_result.append({
    #                 'cnt': cnt,
    #                 'title': article.get('title', ''),
    #                 'description': article.get('description', ''),
    #                 'link': article.get('url', ''),
    #                 'publish_date': article.get('publishedAt', ''),
    #                 'content': content
    #             })
    #     except Exception as e:
    #         print(f"[ERROR] Parsing Failure - ({article.get('url', '')}): {e}")

    save_to_json(json_result, company_name)

    print("\n================[총 결과]================")
    print(f"[INFO] 전체 검색 결과: {total_results} 건")
    print(f"[INFO] 수집된 데이터: {cnt} 건\n")