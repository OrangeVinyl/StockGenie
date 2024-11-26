import os
import time
import psutil
import summarizer
import streamlit as st
from PIL import Image
from util import json_to_csv
from typing import Tuple, Optional
from sentiment import decide_sentiment
from preprocessing import preprocess_json
from crawlers import naver_crawl, news_crawl
from finance.finance_reader import decide_stock_market
from visualizer.finance_visual import run_finance_visual
from models.predict_model_script import run_predict_model
from visualizer.sentiment_visual import run_sentiment_visual


DATA_DIR = "data"
PROCESSED_DIR = os.path.join(DATA_DIR, "processed_articles")
NAVER_DIR = os.path.join(DATA_DIR, "naver_articles")
NEWS_DIR = os.path.join(DATA_DIR, "news_articles")

VALID_SOURCES = {
    '국내': ('naver_crawl', NAVER_DIR, 'naver'),
    '해외': ('news_crawl', NEWS_DIR, 'news')
}

# 성능 측정 함수
def start_performance() -> Tuple[psutil.Process, psutil._common.pcputimes, float]:
    process = psutil.Process(os.getpid())
    start_cpu_times = process.cpu_times()
    start_wall = time.time()
    print("[INFO]: 성능 측정 시작")
    return process, start_cpu_times, start_wall


def measure_performance(start_cpu_times: psutil._common.pcputimes, start_wall: float,
                        end_cpu_times: psutil._common.pcputimes, end_wall: float) -> None:
    user_time = end_cpu_times.user - start_cpu_times.user
    system_time = end_cpu_times.system - start_cpu_times.system
    total_cpu_time = user_time + system_time
    wall_time = end_wall - start_wall

    st.sidebar.header("📜 실행 로그")
    st.sidebar.write(
        f"[INFO]: CPU times: user {user_time:.2f} s, sys {system_time:.2f} s, total: {total_cpu_time:.2f} s")
    st.sidebar.write(f"[INFO]: Wall time: {wall_time:.2f} s")


def ensure_directory(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"[INFO] 디렉토리 생성: {path}")


def crawl_articles(source: str, company_name: str) -> Optional[Tuple[str, str, str]]:
    try:
        crawl_function, input_dir, crawl_domain = VALID_SOURCES[source]
        st.success(f"{source} 뉴스를 크롤링합니다...")
        if crawl_function == 'naver_crawl':
            naver_crawl.run(company_name)
        elif crawl_function == 'news_crawl':
            news_crawl.run(company_name)
        else:
            st.error("[ERROR] 알 수 없는 크롤러입니다.")
            return None
        st.success("뉴스 크롤링이 완료되었습니다.")
        return input_dir, crawl_domain, company_name
    except Exception as e:
        st.error(f"[ERROR] 크롤링 중 오류 발생: {e}")
        return None


def summarize_articles(input_dir: str, output_dir: str, company_name: str, source: str) -> None:
    print("\n===== [기사 요약] =====")
    summarizer.run(input_dir, output_dir, company_name, source)


def main():
    # 페이지 설정
    st.set_page_config(page_title="주식 뉴스 분석 애플리케이션", layout="wide", initial_sidebar_state="expanded")

    # 로고 추가 (옵션)
    if os.path.exists("logo.png"):
        logo = Image.open("logo.png")
        st.image(logo, width=150)

    st.title("STOCKGEINE")
    st.markdown("""
    ### 💡 생성형AI를 활용한 주식 예측 프로그램 개발
    """)
    st.info("선택한 시장에서 기업 관련 뉴스를 크롤링하고, 요약하며, 감성 분석과 주가 예측을 수행합니다.")

    st.markdown("""
    ### **주요 기능**
    - 📰 뉴스 크롤링
    - ✂️ 기사 요약
    - 📊 감성 분석
    - 🔮 주가 예측
    - 📉 결과 시각화
    """)
    st.markdown("---")
    # 사이드바에 입력 정보 배치
    st.sidebar.header("📥 입력 정보")
    source = st.sidebar.selectbox('시장 유형을 선택하세요', ['국내', '해외'])
    company_name = st.sidebar.text_input("기업 이름을 입력하세요")

    st.sidebar.markdown("---")
    st.sidebar.info("이 애플리케이션은 주식 관련 뉴스를 크롤링하고, 요약하며, 감성 분석 및 주가 예측을 수행합니다.")

    # 디렉토리 설정
    ensure_directory(PROCESSED_DIR)

    if st.sidebar.button("프로세스 시작"):
        if not company_name:
            st.sidebar.error("기업 이름을 입력해주세요.")
            st.stop()

        with st.spinner("프로세스를 시작합니다..."):
            # 성능 측정 시작
            process, start_cpu_times, start_wall = start_performance()

            # 진행 상황 표시기 초기화
            progress_bar = st.sidebar.progress(0)
            steps = 7
            step = 0

            # 뉴스 크롤링
            crawl_result = crawl_articles(source, company_name)
            if not crawl_result:
                st.sidebar.error("크롤링에 실패하여 프로그램을 종료합니다.")
                st.stop()
            step += 1
            progress_bar.progress(step / steps)

            input_dir, crawl_domain, company_name = crawl_result
            st.write(
                f"📂 **입력 디렉토리**: {input_dir} \n"
                f"🌐 **크롤 도메인**: {crawl_domain} \n"
                f"🏢 **기업 이름**: {company_name} \n"
                f"📈 **시장 유형**: {source}"
            )

            summarize_articles(input_dir, PROCESSED_DIR, company_name, crawl_domain)
            step += 1
            progress_bar.progress(step / steps)

            try:
                preprocess_json(source, PROCESSED_DIR, company_name)
                step += 1
                progress_bar.progress(step / steps)

                decide_sentiment(source, PROCESSED_DIR, company_name)
                st.success("감성 분석이 완료되었습니다.", icon="✅")
                step += 1
                progress_bar.progress(step / steps)

                json_to_csv.run(company_name, crawl_domain)
                step += 1
                progress_bar.progress(step / steps)

                decide_stock_market(source, company_name)
                st.success("주식 시장 유형을 결정했습니다.", icon="✅")
                step += 1
                progress_bar.progress(step / steps)

                run_predict_model(company_name, source)
                st.success("주가 예측 모델이 실행되었습니다.", icon="✅")
                step += 1
                progress_bar.progress(step / steps)

                run_sentiment_visual(company_name)
                run_finance_visual(company_name)
                st.success("시각화가 완료되었습니다.", icon="✅")
                step += 1
            except Exception as e:
                st.error(f"[ERROR]: 처리 중 오류 발생: {e}")
            finally:
                measure_performance(start_cpu_times, start_wall, process.cpu_times(), time.time())
                progress_bar.empty()
                st.success("프로세스가 성공적으로 완료되었습니다!", icon="✅")


    tabs = st.tabs(["📄 요약된 기사", "📊 감성 분석", "📈 주식 분석", "🔮 예측 모델"])
    with tabs[0]:
        st.header("📄 요약된 기사")
        # num_articles = st.slider("표시할 기사 수", min_value=1, max_value=20, value=5)

    with tabs[1]:
        st.header("📊 감성 분석 결과")
        if company_name and os.path.exists(os.path.join(DATA_DIR, 'csv_datasets', f"{company_name}_datasets.csv")):
            fig1, fig2, fig3, fig4 = run_sentiment_visual(company_name)
            if fig1 and fig2 and fig3 and fig4:
                st.plotly_chart(fig1, use_container_width=True)
                st.plotly_chart(fig2, use_container_width=True)
                st.pyplot(fig3)
                st.pyplot(fig4)
            else:
                st.warning("감성 분석 시각화가 불가능합니다.", icon="⚠️")
        else:
            st.warning("감성 분석 결과가 없습니다. 먼저 프로세스를 실행해주세요.", icon="⚠️")

    with tabs[2]:
        st.header("📈 금융 데이터 분석 결과")
        if company_name and os.path.exists(os.path.join(DATA_DIR, 'stocks', f"{company_name}_stock_dataset.csv")):
            fig1, fig2, fig3, fig4 = run_finance_visual(company_name)
            if fig1 and fig2 and fig3 and fig4:
                st.pyplot(fig1)
                st.pyplot(fig2)
                st.plotly_chart(fig3, use_container_width=True)
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.warning("금융 데이터 분석 시각화가 불가능합니다.", icon="⚠️")
        else:
            st.warning("금융 데이터 분석 결과가 없습니다. 먼저 프로세스를 실행해주세요.", icon="⚠️")

    with tabs[3]:
        st.header("🔮 예측 모델 결과")
        # 예측 모델 결과 표시 로직 추가
        st.write("예측 모델 결과가 여기에 표시됩니다.")

    # 푸터 추가
    st.markdown("""
    ---
    Developed by [SuhwanChoi](https://yourwebsite.com) for iMCapital
    """)

if __name__ == '__main__':
    main()

