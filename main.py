import os
from crawlers import naver_news_crawl, investing_crawl

def main():
    source = input('기업 분류를 선택하세요 (국내/해외): ')
    company_name = input("기업 이름을 입력하세요 : ")

    if source == '국내':
        naver_news_crawl.run(company_name)
        input_dir = os.path.join("data", "naver_articles")

    elif source == '해외':
        return


if  __name__ == '__main__':
    main()