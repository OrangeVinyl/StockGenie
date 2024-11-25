import os
import time
import psutil
import summarizer
from util import json_to_csv
from sentiment import decide_sentiment
from preprocessing import preprocess_json
from crawlers import naver_crawl, news_crawl
from finance.finance_reader import decide_stock_market

def start_performance():
    """
    @description: 성능 측정을 위한 시작 시간과 CPU 시간을 측정하는 함수
    """
    process = psutil.Process()
    start_cpu_times = process.cpu_times()
    start_wall = time.time()

    return process, start_cpu_times, start_wall

def measure_performance(start_cpu_times, start_wall, end_cpu_times, end_wall):
    """
    @description: 성능 측정을 종료하고 측정하기 위한 함수

    :param start_cpu_times:
    :param start_wall:
    :param end_cpu_times:
    :param end_wall:
    """
    user_time = end_cpu_times.user - start_cpu_times.user
    system_time = end_cpu_times.system - start_cpu_times.system
    total_cpu_time = user_time + system_time

    wall_time = end_wall - start_wall

    print("\n======================================================================")
    print(f"CPU times: user {user_time:.2f} s, sys {system_time:.2f} s, total: {total_cpu_time:.2f} s")
    print(f"Wall time: {wall_time:.2f} s")
    print("======================================================================\n")

def get_user_input():
    source = input('시장 유형을 선택하세요 (국내/해외): ').strip()
    company_name = input("기업 이름을 입력하세요 : ").strip()
    return source, company_name

def crawl_articles(source, company_name):
    """
    @description: 뉴스 크롤링을 실행하는 함수

    :param source: 국내 | 해외
    :param company_name: 기업명
    :return: input_dir, crawl_domain, company_name
    """
    if source == '국내':
        print("국내 뉴스를 크롤링합니다...")
        naver_crawl.run(company_name)

        input_dir = os.path.join("data", "naver_articles")
        crawl_domain = 'naver'
    elif source == '해외':
        print("해외 뉴스를 크롤링합니다...")
        news_crawl.run(company_name)

        input_dir = os.path.join("data", "news_articles")
        crawl_domain = 'news'
    else:
        print("잘못된 소스입니다. '국내' 또는 '해외'를 입력해주세요.")
        return None, None, None
    return input_dir, crawl_domain, company_name

def summarize_articles(input_dir, output_dir, company_name, source):
    """
    @description: 기사를 요약하는 함수

    :param input_dir:
    :param output_dir:
    :param company_name:
    :param source:
    """
    print("\n[기사 요약]==============================")
    summarizer.run(input_dir, output_dir, company_name, source)

def main():
    output_dir = os.path.join("data", "processed_articles")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    process, start_cpu_times, start_wall = start_performance()

    source, company_name = get_user_input()

    input_dir, crawl_domain, company_name = crawl_articles(source, company_name)

    print(input_dir, output_dir, company_name, source, crawl_domain)

    summarize_articles(input_dir, output_dir, company_name, crawl_domain)

    preprocess_json(source, output_dir, company_name)

    decide_sentiment(source, output_dir, company_name)

    json_to_csv.run(company_name, crawl_domain)

    decide_stock_market(source, company_name)

    measure_performance(start_cpu_times, start_wall, process.cpu_times(), time.time())

if  __name__ == '__main__':
    main()