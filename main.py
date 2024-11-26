import os
import time
import psutil
import summarizer
from typing import Tuple, Optional
from util import json_to_csv
from sentiment import decide_sentiment
from preprocessing import preprocess_json
from crawlers import naver_crawl, news_crawl
from finance.finance_reader import decide_stock_market
from visualizer.finance_visual import run_finance_visual
from models.predict_model_script import run_predict_model
from visualizer.sentiment_visual import run_sentiment_visual

"""
CMD에서 실행하는 메인 프로그램
"""

DATA_DIR = "data"
PROCESSED_DIR = os.path.join(DATA_DIR, "processed_articles")
NAVER_DIR = os.path.join(DATA_DIR, "naver_articles")
NEWS_DIR = os.path.join(DATA_DIR, "news_articles")

VALID_SOURCES = {
    '국내': ('naver_crawl', NAVER_DIR, 'naver'),
    '해외': ('news_crawl', NEWS_DIR, 'news')
}


def start_performance() -> Tuple[psutil.Process, psutil._common.pcputimes, float]:
    """
    @description: 성능 측정을 위한 시작 시간과 CPU 시간을 측정하는 함수
    """
    process = psutil.Process(os.getpid())
    start_cpu_times = process.cpu_times()
    start_wall = time.time()
    print("[INFO]: 성능 측정 시작")
    return process, start_cpu_times, start_wall


def measure_performance(start_cpu_times: psutil._common.pcputimes, start_wall: float, end_cpu_times: psutil._common.pcputimes, end_wall: float) -> None:
    """
    @description: 성능 측정을 종료하고 결과를 출력하는 함수

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
    print(f"[INFO]: CPU times: user {user_time:.2f} s, sys {system_time:.2f} s, total: {total_cpu_time:.2f} s")
    print(f"[INFO]: Wall time: {wall_time:.2f} s")
    print("======================================================================\n")


def get_user_input() -> Tuple[str, str]:
    """
    사용자로부터 시장 유형과 기업 이름을 입력받는 함수
    """
    while True:
        source = input('시장 유형을 선택하세요 (국내/해외): ').strip()
        if source in VALID_SOURCES:
            break
        print("[ERROR] 잘못된 소스입니다. '국내' 또는 '해외'를 입력해주세요.")

    company_name = input("기업 이름을 입력하세요: ").strip()
    return source, company_name


def crawl_articles(source: str, company_name: str) -> Optional[Tuple[str, str, str]]:
    """
    @description: 뉴스 크롤링을 실행하는 함수

    :param source: 국내 | 해외
    :param company_name: 기업명
    :return: input_dir, crawl_domain, company_name
    """
    try:
        crawl_function, input_dir, crawl_domain = VALID_SOURCES[source]
        print(f"[INFO] {source} 뉴스를 크롤링합니다...")
        if crawl_function == 'naver_crawl':
            naver_crawl.run(company_name)
        elif crawl_function == 'news_crawl':
            news_crawl.run(company_name)
        else:
            print("[ERROR] 알 수 없는 크롤러입니다.")
            return None
        return input_dir, crawl_domain, company_name
    except Exception as e:
        print(f"[ERROR] 크롤링 중 오류 발생: {e}")
        return None


def summarize_articles(input_dir: str, output_dir: str, company_name: str, source: str) -> None:
    """
    @description: 기사를 요약하는 함수

    :param input_dir:
    :param output_dir:
    :param company_name:
    :param source:
    """
    print("\n===== [기사 요약] =====")
    summarizer.run(input_dir, output_dir, company_name, source)


def ensure_directory(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"[INFO] 디렉토리 생성: {path}")


def main() -> None:
    ensure_directory(PROCESSED_DIR)

    process, start_cpu_times, start_wall = start_performance()

    source, company_name = get_user_input()

    crawl_result = crawl_articles(source, company_name)
    if not crawl_result:
        print("[ERROR]: 크롤링에 실패하여 프로그램을 종료합니다.")
        return

    input_dir, crawl_domain, company_name = crawl_result
    print(
        f"[DEBUG]: 디버깅 정보 - input_dir: {input_dir}, output_dir: {PROCESSED_DIR}, company_name: {company_name}, source: {source}, crawl_domain: {crawl_domain}")

    summarize_articles(input_dir, PROCESSED_DIR, company_name, crawl_domain)

    try:
        preprocess_json(source, PROCESSED_DIR, company_name)
        decide_sentiment(source, PROCESSED_DIR, company_name)
        json_to_csv.run(company_name, crawl_domain)
        decide_stock_market(source, company_name)
        run_predict_model(company_name, source)
        run_sentiment_visual(company_name)
        run_finance_visual(company_name)
    except Exception as e:
        print(f"[ERROR]: 처리 중 오류 발생: {e}")
    finally:
        measure_performance(start_cpu_times, start_wall, process.cpu_times(), time.time())

if  __name__ == '__main__':
    main()