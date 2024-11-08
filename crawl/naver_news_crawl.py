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


# [MODULE 1] 기본 요청 처리 함수
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

# [MODULE 2] 네이버 뉴스 검색 함수
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


# [MODULE 3] 필터링된 게시물 데이터를 가져오는 함수
def get_post_data(post, jsonResult, cnt):
    title = post['title']
    description = post['description']
    org_link = post['originallink']
    link = post['link']

    pDate = datetime.datetime.strptime(post['pubDate'], '%a, %d %b %Y %H:%M:%S +0900')
    pDate = pDate.strftime('%Y-%m-%d %H:%M:%S')

    jsonResult.append({'cnt': cnt, 'title': title, 'description': description,
                       'org_link': org_link, 'link': link, 'pDate': pDate})
    return

# [MODULE 4] 뉴스 본문을 가져오는 함수
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

# [MODULE 5] 뉴스 데이터 필터링 함수 (도메인 검사)
def filter_post(post, keyword):
    title = post['title']
    link = post['link']

    if keyword.lower() in title.lower() and "n.news.naver.com" in link:
        return True
    return False


def main():
    node = 'news'
    src_text = input('검색어를 입력하세요: ')
    cnt = 0
    jsonResult = []

    jsonResponse = get_naver_search(node, src_text, 1, 100)
    total = jsonResponse['total']

    while (jsonResponse is not None) and (jsonResponse['display'] != 0):
        for post in jsonResponse['items']:
            if filter_post(post, src_text):
                cnt += 1
                get_post_data(post, jsonResult, cnt)

        start = jsonResponse['start'] + jsonResponse['display']
        jsonResponse = get_naver_search(node, src_text, start, 100)

    # Multi Threading 본문 크롤링
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_news_content, post['link']): post for post in jsonResult}
        for future in as_completed(future_to_url):
            post = future_to_url[future]
            try:
                content = future.result()
                if content:
                    post['content'] = content
            except Exception as e:
                print(f"Error processing post {post['cnt']}: {e}")

    # 저장 디렉토리 경로 설정
    save_dir = "../data/naver_articles"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 파일 저장 경로 설정
    save_path = os.path.join(save_dir, f'{src_text}_naver_articles.json')


    print("================[총 검색 결과]================")
    print('전체 검색 : %d 건' % total)

    with open(save_path, 'w', encoding='utf8') as outfile:
        retJson = json.dumps(jsonResult, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(retJson)

    print("가져온 데이터 : %d 건" % cnt)
    print('%s_naver_articles.json SAVED' % src_text)
    print(f'{save_path} SAVED')

if __name__ == '__main__':
    main()