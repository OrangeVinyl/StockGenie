import os
import urllib.request
import datetime
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

client_id = os.getenv("NAVER_CLIENT")
client_secret = os.getenv("NAVER_SECRET")

def get_request_url(url):
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)

    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            print("[%s] Url Request Success" % datetime.datetime.now())
            return response.read().decode('utf-8')
    except Exception as e:

        print("================[ END ]================")
        print("[%s] LAST URL : %s" % (datetime.datetime.now(), url))
        print(e)
        return None

def get_naver_search(node, src_text, start, display):
    base = "https://openapi.naver.com/v1/search"
    node = "/" + node + ".json"
    parameters = "?query=%s&start=%s&display=%s" % (urllib.parse.quote(src_text), start, display)

    url = base + node + parameters
    response_decode = get_request_url(url)

    if response_decode is None: ## 에러가 발생 할 수 있음
        return None
    else:
        return json.loads(response_decode)

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
        print(f"Error while crawling news content: {e}")
        return None

def filter_post(post, keyword):
    title = post['title']
    link = post['link']

    if keyword.lower() in title.lower() and "n.news.naver.com" in link:
        return True
    return False


def run(c_name):
    node = 'news'
    src_text = c_name
    cnt = 0
    json_result = []

    json_response = get_naver_search(node, src_text, 1, 100)
    total = json_response['total']

    while (json_response is not None) and (json_response['display'] != 0):
        for post in json_response['items']:
            if filter_post(post, src_text):
                cnt += 1
                get_post_data(post, json_result, cnt)

        start = json_response['start'] + json_response['display']
        json_response = get_naver_search(node, src_text, start, 100)

    # Multi Threading crawling
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_news_content, post['link']): post for post in json_result}
        for future in as_completed(future_to_url):
            post = future_to_url[future]
            try:
                content = future.result()
                if content:
                    post['content'] = content
            except Exception as e:
                print(f"Error processing post {post['cnt']}: {e}")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_dir = os.path.join(base_dir, 'data', 'naver_articles')

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    save_path = os.path.join(save_dir, f'{c_name}_naver_articles.json')


    print("================[총 검색 결과]================")
    print('전체 검색 : %d 건' % total)

    with open(save_path, 'w', encoding='utf8') as outfile:
        res = json.dumps(json_result, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(res)

    print("가져온 데이터 : %d 건" % cnt)
    print('%s_naver_articles.json SAVED' % src_text)
    print(f'{save_path} SAVED')