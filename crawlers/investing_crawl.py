import os
import time
import json
import datetime
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def set_chrome_driver(headless=True):
    options = webdriver.ChromeOptions()

    if headless:
        options.add_argument('headless')
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scroll_down(driver, pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def get_article_content(driver, link):
    driver.get(link)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "article_container"))
        )
        paragraphs = driver.find_elements(By.CSS_SELECTOR, ".article_container p")
        content = " ".join([p.text for p in paragraphs])
    except Exception as e:
        print(f"Error fetching content from {link}: {e}")
        content = "Content not available"

    return content


def get_news_articles(company_name):
    print(f"[{datetime.datetime.now()}] Investing.com 기사 수집을 시작합니다.")

    cnt = 0
    results = []
    base_url = f"https://www.investing.com/search/?q={company_name}&tab=news"
    driver = set_chrome_driver(True)
    driver.get(base_url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".articleItem"))
        )
    except Exception as e:
        print(f"초기 로딩 중 에러 발생: {e}")
        driver.quit()
        return []

    scroll_down(driver)

    article_items = driver.find_elements(By.CSS_SELECTOR, ".articleItem")
    total_articles = len(article_items)

    print(f"총 {total_articles}개의 기사를 발견했습니다.")

    for index, item in enumerate(article_items):
        try:
            title = item.find_element(By.CSS_SELECTOR, ".textDiv a.title").text
            link = item.find_element(By.CSS_SELECTOR, ".textDiv a.title").get_attribute('href')

            # 예외 처리
            description_elements = item.find_elements(By.CSS_SELECTOR, ".textDiv p.js-news-item-content")
            description = description_elements[0].text if description_elements else "Description not available"
            date_elements = item.find_elements(By.CSS_SELECTOR, ".date")
            publish_date = date_elements[0].text if date_elements else "Date not available"

            if "Date not available" in publish_date or "Description not available" in description:
                continue

            cnt += 1

            results.append({
                'cnt': cnt,
                'title': title,
                'description': description.strip(),
                'link': link,
                'publish_date': publish_date
            })

        except Exception as e:
            print(f"Error processing article {index}: {e}")

## 다른 방법 찾아보기 - 속도가 너무 느리다.
    # for article in results:
    #     article['content'] = get_article_content(driver, article['link'])

    driver.quit()

    print(f"총 {cnt}개의 기사를 성공적으로 수집하였습니다.")

    return results

def run(company_name):
    articles = get_news_articles(company_name)

    if not articles:
        print("수집된 기사가 없습니다.")
        return

    # 저장 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_dir = os.path.join(base_dir, 'data', 'investing_articles')

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    save_path = os.path.join(save_dir, f'{company_name}_investing_articles.json')

    # 결과 저장
    with open(save_path, "w", encoding="utf-8") as outfile:
        res = json.dumps(articles, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(res)

    print("================[총 검색 결과]================")
    print(f"가져온 데이터 : {len(articles)} 건")
    print('%s_naver_articles.json SAVED' % company_name)
    print(f'{save_path} SAVED')

