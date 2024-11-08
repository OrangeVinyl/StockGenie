import time
import json
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures

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
    results = []
    base_url = f"https://www.investing.com/search/?q={company_name}&tab=news"
    driver = set_chrome_driver(False)
    driver.get(base_url)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".articleItem"))
    )

    scroll_down(driver)

    article_items = driver.find_elements(By.CSS_SELECTOR, ".articleItem")

    for index, item in enumerate(article_items):
        try:
            title = item.find_element(By.CSS_SELECTOR, ".textDiv a.title").text
            link = item.find_element(By.CSS_SELECTOR, ".textDiv a.title").get_attribute('href')

            # 예외 처리
            description_elements = item.find_elements(By.CSS_SELECTOR, ".textDiv p.js-news-item-content")
            description = description_elements[0].text if description_elements else "Description not available"
            date_elements = item.find_elements(By.CSS_SELECTOR, ".date")
            pDate = date_elements[0].text if date_elements else "Date not available"

            if "Date not available" in pDate or "Description not available" in description:
                continue

            results.append({
                "title": title,
                "description": description.strip(),
                "org_link": link,
                "pDate": pDate
            })


        except Exception as e:
            print(f"Error processing article {index}: {e}")

## 다른 방법 찾아보기 - 속도가 너무 느리다.
    # for article in results:
    #     article['content'] = get_article_content(driver, article['org_link'])

    driver.quit()

    with open("%s_investing_articles.json" % company_name, "w", encoding="utf-8") as outfile:
        retJson = json.dumps(results, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(retJson)

    return results

def main():
    company_name = input('검색어를 입력하세요: ')
    articles = get_news_articles(company_name)
    print(articles)

if __name__ == '__main__':
    main()