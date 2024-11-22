import os
import json
import logging
import datetime
import requests
import urllib.request
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

client_id = os.getenv("NAVER_CLIENT")
client_secret = os.getenv("NAVER_SECRET")

limit_days = 30 # 가져올 날짜 수

def get_request_url(url):
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)

    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            return response.read().decode('utf-8')
    except Exception as e:
        print("[INFO] [%s] LAST URL : %s" % (datetime.datetime.now(), url))
        return None

def get_naver_search(company_name, start, display):
    base = "https://openapi.naver.com/v1/search/news.json"
    parameters = "?query=%s&start=%s&display=%s&sort=sim" % (urllib.parse.quote(company_name), start, display)

    url = base + parameters
    response = get_request_url(url)

    if response is not None:
        return json.loads(response)

def get_post_data(post, json_result, cnt):
    title = post['title']
    description = post['description']
    org_link = post['originallink']
    link = post['link']

    publish_date = datetime.datetime.strptime(post['pubDate'], '%a, %d %b %Y %H:%M:%S +0900')
    publish_date = publish_date.strftime('%Y-%m-%d %H:%M:%S')

    json_result.append({'cnt': cnt, 'title': title, 'description': description,
                       'org_link': org_link, 'link': link, 'publish_date': publish_date})
    return

def get_news_content(link):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(link, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.find('div', {'id': 'newsct_article'})  # 네이버 뉴스 본문 영역
            if content:
                return content.get_text(strip=True)
        return None

    except Exception as e:
        print(f"[ERROR] Error while crawling news content: {e}")
        return None

def filter_post(post, keyword, cutoff_date):
    title = post['title']
    link = post['link']
    pub_date = datetime.datetime.strptime(post['pubDate'], '%a, %d %b %Y %H:%M:%S +0900')

    if (keyword.lower() in title.lower() and
        "n.news.naver.com" in link and
        pub_date >= cutoff_date):
        return True
    return False

def save_output(json_result, c_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_dir = os.path.join(base_dir, 'data', 'naver_articles')

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    save_path = os.path.join(save_dir, f'{c_name}_naver_articles.json')

    with open(save_path, 'w', encoding='utf8') as outfile:
        res = json.dumps(json_result, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(res)

    print('[SUCCESS] %s_naver_articles.json SAVED' % c_name)
    print(f'[SUCCESS] {save_path} SAVED')

def run(company_name):
    # 기사 수집을 위한 변수 초기화
    today = datetime.datetime.now()
    one_week_ago = today - datetime.timedelta(days=limit_days)

    cnt = 0
    start = 1 # 검색 시작 위치 (1~1000)
    display = 100 # 검색 결과 출력 건수 (10~100)
    total = 0 # 검색 결과 총 건수

    json_result = []

    # 각 날짜별 기사 수를 저장할 딕셔너리 초기화
    articles_per_day = {}
    for i in range(limit_days):
        day = (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        articles_per_day[day] = 0

    while True:
        json_response = get_naver_search(company_name, start, display)

        if json_response is None or json_response.get('display', 0) == 0:
            print("[WARN] 더 이상 가져올 기사가 없습니다.")
            break

        if total == 0:
            total = json_response.get('total', 0)

        items = json_response.get('items', [])
        if not items:
            break

        for post in items:
            pub_date = datetime.datetime.strptime(post['pubDate'], '%a, %d %b %Y %H:%M:%S +0900')

            if pub_date < one_week_ago:
                continue

            date_str = pub_date.strftime('%Y-%m-%d')
            if date_str in articles_per_day:
                articles_per_day[date_str] += 1

            if filter_post(post, company_name, one_week_ago):
                cnt += 1
                get_post_data(post, json_result, cnt)

        if all(count >= 1 for count in articles_per_day.values()) and cnt >= 20:
            break

        if cnt >= 300:
            break

        start += display

        if start > 1000:
            print("[WARN] 네이버 API의 최대 검색 한도에 도달했습니다.")
            break

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_post = {executor.submit(get_news_content, post['link']): post for post in json_result}

        for future in as_completed(future_to_post):
            post = future_to_post[future]
            try:
                content = future.result()
                if content:
                    post['content'] = content
            except Exception as e:
                logging.error(f"[ERROR] ThreadPoolExecutor error: {e}")

    save_output(json_result, company_name)

    print("\n===== [검색 결과] =====")
    print("[INFO] 전체 검색 결과 : %d 건" % total)
    print("[INFO] 가져온 데이터 : %d 건" % cnt)
    print("[INFO] 날짜별 기사 수 :")
    for date_str, count in sorted(articles_per_day.items()):
        print(f"{date_str}: {count}건")


def test_naver_crawl():
    run('삼성전자')
    # run('SK하이닉스')
    # run('LG에너지솔루션')
    # run('셀트리온')