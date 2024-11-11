import os
import json
from tqdm import tqdm
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from .prompts import custom_prompt_template

def load_articles(input_dir, company_name, source):
    articles = []

    if source == 'naver':
        file_pattern = f"{company_name}_naver_articles"
    elif source == 'investing':
        file_pattern = f"{company_name}_investing_articles"
    else:
        print("지원하지 않는 소스입니다.")
        return articles

    for filename in os.listdir(input_dir):
        if filename.startswith(file_pattern) and filename.endswith(".json"):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                articles.extend(data)
    return articles

def save_articles(articles, output_dir, company_name, source):
    output_file = os.path.join(output_dir, f"{company_name}_{source}_summarized_articles.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

    print(f"요약된 기사가 {output_file}에 저장되었습니다.")

def summarize_article(content, chain):
    if not content:
        return "요약할 내용이 없습니다."

    # 텍스트 분할
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    texts = text_splitter.split_text(content)

    docs = [Document(page_content=t) for t in texts]

    summary = chain.invoke({'input_documents': docs})['output_text']
    return summary.strip()

def run(input_dir, output_dir, company_name, source):
    from dotenv import load_dotenv
    load_dotenv()

    set_llm_cache(InMemoryCache())

    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=custom_prompt_template)

    articles = load_articles(input_dir, company_name, source)
    if not articles:
        print("요약할 기사가 없습니다.")
        return

    for article in tqdm(articles, desc="기사 요약 중"):
        if 'summary' not in article or not article['summary']:
            content = article.get('content', '')
            summary = summarize_article(content, chain)
            article['summary'] = summary

    save_articles(articles, output_dir, company_name, source)

