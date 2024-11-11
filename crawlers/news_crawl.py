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

def fetch_news(api_key, query, from_date, to_date, language='en', page_size=100, page=1):
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': query,
        'from': from_date,
        'to': to_date,
        'language': language,
        'pageSize': page_size,
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

    logging.info(article)

    title = (article.get('title') or '').lower()
    description = (article.get('description') or '').lower()
    published_at = article.get('publishedAt', '') or ''

    try:
        pub_date = datetime.datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        logging.warning(f"[WARN] 잘못된 날짜 형식 : {published_at}")
        return False

    if (query.lower() in title or query.lower() in description) and pub_date >= cutoff_date:
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

    logging.info('%s_news_articles.json SAVED' % company_name)
    logging.info(f'{save_path} SAVED')


def run(company_name):

    today = datetime.datetime.utcnow()
    seven_days_ago = today - datetime.timedelta(days=7)

    from_date = seven_days_ago.strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    all_articles = []
    page = 1
    total_results = 0
    json_result = []
    cnt = 0

    data = fetch_news(API_KEY, company_name, from_date, to_date, page=page)
    if data:
        articles = data.get('articles', [])
        for article in articles:
            if filter_article(article, company_name, seven_days_ago):
                all_articles.append(article)

        total_results = data.get('totalResults', 0)
        logging.info(f"페이지 {page}: {len(articles)}개 기사 중 {len(all_articles)}개 필터링됨.")

    logging.info(f"총 {len(all_articles)}개의 기사를 찾았습니다.")

    ## Multi Threading
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
                logging.info(f"[ERROR] ThreadPoolExecutor - ({article.get('url', '')}): {e}")

    save_to_json(json_result, company_name)

    logging.info("\n================[총 검색 결과]================")
    logging.info(f"전체 검색: {total_results} 건")
    logging.info(f"가져온 데이터: {cnt} 건\n")
