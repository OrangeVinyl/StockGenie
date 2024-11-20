import os
import json

from langchain_core.prompts import PromptTemplate
from tqdm import tqdm
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from .prompts import CUSTOM_PROMPT, EN_CUSTOM_PROMPT

def load_articles(input_dir, company_name, source):
    """
    @description:

    :param input_dir:
    :param company_name:
    :param source:
    :return: articles
    """
    articles = []

    if source == 'naver':
        file_pattern = f"{company_name}_naver_articles"
    elif source == 'investing':
        file_pattern = f"{company_name}_investing_articles"
    elif source == 'news':
        file_pattern = f"{company_name}_news_articles"
    else:
        print("[WARN] 지원하지 않는 소스입니다.")
        return articles

    for filename in os.listdir(input_dir):
        if filename.startswith(file_pattern) and filename.endswith(".json"):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                articles.extend(data)

    return articles

def save_articles(articles, output_dir, company_name, source):
    """
    @description:

    :param articles:
    :param output_dir:
    :param company_name:
    :param source:
    :return:
    """
    output_file = os.path.join(output_dir, f"{company_name}_{source}_summarized_articles.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

    print(f"[SUCCESS] 요약된 기사가 {output_file}에 저장되었습니다.")

def summarize_article(content, chain):
    """
    @description:

    :param content:
    :param chain:
    :return:+
    """
    if not content:
        return "[WARN] 요약할 내용이 없습니다."

    ## Split Text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    texts = text_splitter.split_text(content)

    docs = [Document(page_content=t) for t in texts]

    summary = chain.invoke({'input_documents': docs})['output_text']
    return summary.strip()

def clean_source_files(input_dir, company_name, source):
    """
    @description 각 소스 디렉토리에서 처리된 JSON 파일을 제거합니다.
    """
    if source == 'naver':
        file_pattern = f"{company_name}_naver_articles"
    elif source == 'investing':
        file_pattern = f"{company_name}_investing_articles"
    elif source == 'news':
        file_pattern = f"{company_name}_news_articles"
    else:
        print("[WARN] 지원하지 않는 소스입니다.")
        return

    for filename in os.listdir(input_dir):
        if filename.startswith(file_pattern) and filename.endswith(".json"):
            file_path = os.path.join(input_dir, filename)
            try:
                os.remove(file_path)
                print(f"[SUCCESS] 기존 파일 제거: {file_path}")
            except Exception as e:
                print(f"[ERROR] Error removing file {file_path}: {e}")

def run(input_dir, output_dir, company_name, source):
    from dotenv import load_dotenv
    load_dotenv()
    set_llm_cache(InMemoryCache()) #Cache

    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ## LangChain - load_summarize_chain
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt_template = None

    if source == 'naver':
        prompt_template = PromptTemplate(template=CUSTOM_PROMPT, input_variables=["text"])
    elif source == 'news':
        prompt_template = PromptTemplate(template=EN_CUSTOM_PROMPT, input_variables=["text"])

    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt_template)

    articles = load_articles(input_dir, company_name, source)
    if not articles:
        print("[WARN] 요약할 기사가 없습니다.")
        return

    ## tqdm Progress Bar
    for article in tqdm(articles, desc="기사 요약 중"):
        if 'summary' not in article or not article['summary']:
            content = article.get('content', '')
            summary = summarize_article(content, chain)
            article['summary'] = summary

    save_articles(articles, output_dir, company_name, source)

    clean_source_files(input_dir, company_name, source)