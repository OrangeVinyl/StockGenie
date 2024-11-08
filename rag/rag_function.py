import os
import tempfile

from dotenv import load_dotenv
from langchain_community.document_loaders import WikipediaLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def load_docs(query):
    loader = WikipediaLoader(query=query, load_max_docs=1)
    documents = loader.load()

    # 디버깅: 문서가 제대로 로드되었는지 확인
    if not documents or len(documents) == 0:
        print("No documents loaded. Check the query or WikipediaLoader.")
        raise ValueError("No documents loaded. The 'documents' list is empty.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)

    # 디버깅: splits 리스트가 제대로 생성되었는지 확인
    if not splits or len(splits) == 0:
        print("Splits list is empty. Check the text splitting logic.")
        raise ValueError("The 'splits' list is empty after splitting the documents.")

    return splits


def create_vectorstore(splits):
    embeddings = OpenAIEmbeddings()

    # Ensure that splits is not empty and is properly formatted
    if not splits or len(splits) == 0:
        raise ValueError("The 'splits' list is empty or not properly formatted.")

    with tempfile.TemporaryDirectory() as persist_directory:
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=persist_directory
        )


    return vectorstore


def create_rag_chain(vectorstore):
    llm = ChatOpenAI(model='gpt-4o', temperature=0)

    prompt_template = """
    아래의 문맥을 사용하여 질문에 답하시오.
    만약 답을 모른다면, 모른다고 말하고 답을 지어내지 마십시오.
    최대한 세 문장으로 답하고 가능한 한 간결하게 유지하십시오.
    {context}
    질문: {question}
    유용한 답변:
    """

    PROMPT = PromptTemplate(template = prompt_template, input_variables=['context', 'question'])

    chain_type_kwargs = {"prompt": PROMPT}

    qa_chain = RetrievalQA.from_chain_type(
        llm= llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs=chain_type_kwargs,
        return_source_documents=True
    )

    return qa_chain