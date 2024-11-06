import requests
import json
import os
from dotenv import load_dotenv

# 환경변수로 API 키 관리
load_dotenv()
GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")


def get_guardian_articles(company_name, api_key):
    base_url = "https://content.guardianapis.com/search"
    params = {
        "q": company_name,
        "api-key": api_key,
        "show-fields": "headline,body,thumbnail"
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        articles = data['response']['results']

        for idx, article in enumerate(articles):
            title = article['webTitle']
            link = article['webUrl']
            body = article['fields'].get('body', '본문 없음')
            print(f"[{idx + 1}] 제목: {title}\n링크: {link}\n본문 요약: {body[:200]}...\n")

    else:
        print(f"HTTP Error: {response.status_code}")


if __name__ == "__main__":
    company_name = input("검색할 기업명을 입력하세요: ")
    get_guardian_articles(company_name, GUARDIAN_API_KEY)