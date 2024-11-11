import os
from crawlers import naver_crawl, investing_crawl
from summarizer import summarizer

def main():
    global input_dir

    source = input('기업 분류를 선택하세요 (국내/해외): ')
    company_name = input("기업 이름을 입력하세요 : ")

    if source == '국내':
        print("네이버 뉴스를 크롤링합니다...")
        naver_crawl.run(company_name)
        input_dir = os.path.join("data", "naver_articles")

    elif source == '해외':
        print("Investing 뉴스를 크롤링합니다...")
        investing_crawl.run(company_name)
        input_dir = os.path.join("data", "investing_articles")

    print("기사를 요약합니다...")
    output_dir = os.path.join("data", "processed_articles")
    summarizer.run(input_dir, output_dir, company_name, 'naver')


if  __name__ == '__main__':
    main()