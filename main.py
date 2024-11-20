import os
import time
import psutil
import summarizer
from sentiment import decide_sentiment
from preprocessing import preprocess_json
from crawlers import naver_crawl, news_crawl

def start_performance():
    process = psutil.Process()
    start_cpu_times = process.cpu_times()
    start_wall = time.time()

    return process, start_cpu_times, start_wall

def measure_performance(start_cpu_times, start_wall, end_cpu_times, end_wall):
    user_time = end_cpu_times.user - start_cpu_times.user
    system_time = end_cpu_times.system - start_cpu_times.system
    total_cpu_time = user_time + system_time

    wall_time = end_wall - start_wall

    print("\n======================================================================")
    print(f"CPU times: user {user_time:.2f} s, sys {system_time:.2f} s, total: {total_cpu_time:.2f} s")
    print(f"Wall time: {wall_time:.2f} s")
    print("======================================================================\n")

def get_user_input():
    source = input('기업 분류를 선택하세요 (국내/해외): ').strip()
    company_name = input("기업 이름을 입력하세요 : ").strip()
    return source, company_name

def crawl_articles(source, company_name):
    if source == '국내':
        print("국내 뉴스를 크롤링합니다...")
        naver_crawl.run(company_name)

        # TODO: run에서 return한 값으로 input_dir, crawl_domain 설정
        input_dir = os.path.join("data", "naver_articles")
        crawl_domain = 'naver'
    elif source == '해외':
        print("해외 뉴스를 크롤링합니다...")
        news_crawl.run(company_name)

        # TODO: run에서 return한 값으로 input_dir, crawl_domain 설정
        input_dir = os.path.join("data", "news_articles")
        crawl_domain = 'news'
    else:
        print("잘못된 소스입니다. '국내' 또는 '해외'를 입력해주세요.")
        return None, None, None
    return input_dir, crawl_domain, company_name

def summarize_articles(input_dir, output_dir, company_name, source):
    print("\n[기사 요약]==============================")
    summarizer.run(input_dir, output_dir, company_name, source)

def main():
    output_dir = os.path.join("data", "processed_articles")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    process, start_cpu_times, start_wall = start_performance()

    source, company_name = get_user_input()

    input_dir, crawl_domain, company_name = crawl_articles(source, company_name)

    summarize_articles(input_dir, output_dir, company_name, crawl_domain)

    preprocess_json(source, output_dir, company_name)

    decide_sentiment(source, output_dir, company_name)

    measure_performance(start_cpu_times, start_wall, process.cpu_times(), time.time())

if  __name__ == '__main__':
    main()