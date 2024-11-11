from langchain.prompts import PromptTemplate

CUSTOM_PROMPT ="""다음 텍스트를 읽고, 핵심 내용을 한국어로 2~3문장으로 요약해 주세요:

{text}
"""

custom_prompt_template = PromptTemplate(template=CUSTOM_PROMPT, input_variables=["text"])