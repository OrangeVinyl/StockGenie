import streamlit as st
from rag_function import load_docs, create_vectorstore, create_rag_chain

st.title('Ex. RAG Q&A System')

topic = st.text_input('위키피디아 주제를 입력하세요:')
question = st.text_input('해당 주제에 대해 질문하세요:')

if topic and question:
    if st.button("답변 받기"):
        with st.spinner('로딩 중...'):
            splits = load_docs(topic)
            vectorstore = create_vectorstore(splits)
            qa_chain = create_rag_chain(vectorstore)

            result = qa_chain.invoke({"query": question})

            st.subheader("답변: ")
            st.write(result["result"])

            st.write("---")

st.sidebar.title("소개")
st.sidebar.info(
    "이 앱은 RAG(검색 증강 생성) 시스템을 시연합니다. "
    "위키피디아를 지식 소스로 사용하고 OpenAI의 GPT 모델을 통해 답변을 생성합니다."
)