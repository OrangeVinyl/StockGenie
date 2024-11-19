import os
import time
import psutil
from crawlers import naver_crawl , news_crawl
import summarizer

def get_user_input():
    source = input('기업 분류를 선택하세요 (국내/해외): ').strip()
    company_name = input("기업 이름을 입력하세요 : ").strip()
    return source, company_name

def crawl_articles(source, company_name):
    if source == '국내':
        print("국내 뉴스를 크롤링합니다...")
        naver_crawl.run(company_name)
        input_dir = os.path.join("data", "naver_articles")
        crawl_source = 'naver'
    elif source == '해외':
        print("해외 뉴스를 크롤링합니다...")
        news_crawl.run(company_name)
        input_dir = os.path.join("data", "news_articles")
        crawl_source = 'news'
    else:
        print("잘못된 소스입니다. '국내' 또는 '해외'를 입력해주세요.")
        return None, None, None
    return input_dir, crawl_source, company_name

def summarize_articles(input_dir, output_dir, company_name, source):
    print("기사를 요약합니다...")
    summarizer.run(input_dir, output_dir, company_name, source)

def measure_performance(start_cpu_times, start_wall, end_cpu_times, end_wall):
    user_time = end_cpu_times.user - start_cpu_times.user
    system_time = end_cpu_times.system - start_cpu_times.system
    total_cpu_time = user_time + system_time

    wall_time = end_wall - start_wall

    print("\n======================================================================")
    print(f"CPU times: user {user_time:.2f} s, sys {system_time:.2f} s, total: {total_cpu_time:.2f} s")
    print(f"Wall time: {wall_time:.2f} s")
    print("======================================================================\n")

def main():
    process = psutil.Process()
    start_cpu_times = process.cpu_times()
    start_wall = time.time()

    source, company_name = get_user_input()

    input_dir, crawl_source, company_name = crawl_articles(source, company_name)
    if input_dir is None:
        return

    output_dir = os.path.join("data", "processed_articles")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    summarize_articles(input_dir, output_dir, company_name, crawl_source)


    end_cpu_times = process.cpu_times()
    end_wall = time.time()
    measure_performance(start_cpu_times, start_wall, end_cpu_times, end_wall)

if  __name__ == '__main__':
    main()