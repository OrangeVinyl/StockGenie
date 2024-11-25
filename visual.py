import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)

ARTICLE_SAVE_PATH = os.path.join(BASE_DIR, 'data', 'processed_articles')
print("ARTICLE_SAVE_PATH:", ARTICLE_SAVE_PATH)

total_path = os.path.join(ARTICLE_SAVE_PATH, 'SK하이닉스_naver_summarized_article.csv')
print("total_path:", total_path)

# with open(total_path, "r", encoding="utf-8") as f:
#     data = json.load(f)
#     print(data)