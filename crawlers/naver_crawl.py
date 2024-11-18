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
            print("[SUCCESS] [%s] Url Request Success" % datetime.datetime.now())
            return response.read().decode('utf-8')
    except Exception as e:
        print()
        print("================[ END ]================")
        print("[INFO] [%s] LAST URL : %s" % (datetime.datetime.now(), url))
        return None

def get_naver_search(node, src_text, start, display):
    base = "https://openapi.naver.com/v1/search"
    node = "/" + node + ".json"

    parameters = "?query=%s&start=%s&display=%s&sort=date" % (urllib.parse.quote(src_text), start, display)

    url = base + node + parameters
    response_decode = get_request_url(url)

    if response_decode is None:
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
        print(f"[ERROR] Error while crawling news content: {e}")
        return None

def filter_post(post, keyword, cutoff_date):
    title = post['title']
    link = post['link']
    pub_date = datetime.datetime.strptime(post['pubDate'], '%a, %d %b %Y %H:%M:%S +0900')

    # 키워드 포함, 네이버 뉴스 링크, 최근 1주일 내 게시된 기사
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

def run(c_name):
    node = 'news'
    src_text = c_name
    cnt = 0
    json_result = []

    today = datetime.datetime.now()
    one_week_ago = today - datetime.timedelta(weeks=1)

    json_response = get_naver_search(node, src_text, 1, 100)
    if json_response is None:
        print("[WARN] 검색 결과를 가져오지 못했습니다.")
        return

    total = json_response.get('total', 0)

    while (json_response is not None) and (json_response.get('display', 0) != 0):
        for post in json_response.get('items', []):
            if filter_post(post, src_text, one_week_ago):
                cnt += 1
                get_post_data(post, json_result, cnt)
            else:
                ## At least 1 week
                pub_date = datetime.datetime.strptime(post['pubDate'], '%a, %d %b %Y %H:%M:%S +0900')
                if pub_date < one_week_ago:
                    print("[WARN] 1주일 이전의 기사를 만나 검색을 종료합니다.")
                    break

        if any(datetime.datetime.strptime(post['pubDate'], '%a, %d %b %Y %H:%M:%S +0900') < one_week_ago for post in json_response.get('items', [])):
            break

        start = json_response['start'] + json_response['display']
        json_response = get_naver_search(node, src_text, start, 100)

    ## Multi Threading
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_news_content, post['link']): post for post in json_result}
        for future in as_completed(future_to_url):
            post = future_to_url[future]
            try:
                content = future.result()
                if content:
                    post['content'] = content
            except Exception as e:
                print(f"[ERROR] Error processing post {post['cnt']}: {e}")

    save_output(json_result, c_name)

    print("\n================[총 검색 결과]================")
    print("[INFO] 전체 검색 : %d 건" % total)
    print("[INFO] 가져온 데이터 : %d 건" % cnt)
