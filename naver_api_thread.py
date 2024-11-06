import os
import urllib.request
import datetime
import json
import ssl
from bs4 import BeautifulSoup
import concurrent.futures

from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("NAVER_CLIENT")
client_secret = os.getenv("NAVER_SECRET")

# [CODE 1]
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
        print(e)
        print("[%s] Error for URL : %s" % (datetime.datetime.now(), url))
        return None


# [CODE 2]
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


# [CODE 3] 본문 데이터 수집
def get_article_content(link):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    try:
        req = urllib.request.Request(link, headers=headers)
        response = urllib.request.urlopen(req)
        soup = BeautifulSoup(response, 'html.parser')

        # 다양한 태그와 클래스 탐색 (자주 사용되는 본문 태그들)
        selectors = [
            ('div', {'id': 'articleBodyContents'}),
            ('div', {'class': 'article-content'}),
            ('section', {'id': 'article-body'}),
            ('div', {'id': 'newsEndContents'}),
            # 필요 시 더 많은 태그를 추가
        ]

        main_content = None
        for tag, attrs in selectors:
            main_content = soup.find(tag, attrs)
            if main_content:
                break

        if main_content:
            return main_content.get_text(strip=True)
        else:
            return "본문을 가져올 수 없습니다."

    except Exception as e:
        print(f"본문 크롤링 오류: {e}")
        return "본문을 가져오는 중 오류 발생"


# [CODE 4] 게시글 데이터 수집
def get_post_data(post, jsonResult, cnt):
    title = post['title']
    description = post['description']
    org_link = post['originallink']
    link = post['link']

    try:
        content = get_article_content(link)  # 본문을 가져오는 함수 호출
    except Exception as e:
        content = "본문을 가져올 수 없습니다."  # 본문 크롤링 오류 발생 시 기본 메시지 설정
        print(f"[ERROR] 본문을 가져오는 데 실패했습니다. 링크: {link}, 오류: {e}")

    post_date = datetime.datetime.strptime(post['pubDate'], '%a, %d %b %Y %H:%M:%S +0900')
    post_date = post_date.strftime('%Y-%m-%d %H:%M:%S')

    jsonResult.append({
        'cnt': cnt,
        'title': title,
        'description': description,
        'org_link': org_link,
        'link': link,
        'post_date': post_date,
        'content': content
    })


# [CODE 5] 멀티스레딩을 사용한 본문 크롤링
def fetch_all_contents(posts, jsonResult):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_post_data, post, jsonResult, idx + 1) for idx, post in enumerate(posts)]
        concurrent.futures.wait(futures)


def main():
    node = 'news'
    src_text = input('검색어를 입력하세요: ')
    cnt = 0
    jsonResult = []

    jsonResponse = get_naver_search(node, src_text, 1, 100)
    if jsonResponse is None or jsonResponse['display'] == 0:
        print("데이터를 가져오지 못했습니다.")
        return

    total = jsonResponse['total']
    print('전체 검색 : %d 건' % total)

    # 멀티스레딩을 이용해 본문 데이터를 수집
    posts = jsonResponse['items']
    fetch_all_contents(posts, jsonResult)

    # JSON 결과 파일 저장
    with open('%s_naver_%s.json' % (src_text, node), 'w', encoding='utf8') as outfile:
        retJson = json.dumps(jsonResult, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(retJson)

    print("가져온 데이터 : %d 건" % len(jsonResult))
    print('%s_naver_%s.json SAVED' % (src_text, node))


if __name__ == '__main__':
    main()