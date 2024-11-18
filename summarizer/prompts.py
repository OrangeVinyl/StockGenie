from langchain.prompts import PromptTemplate

CUSTOM_PROMPT ="""다음 텍스트를 읽고, 핵심 내용을 입력 언어에 맞춰 5문장으로 요약해 주세요.
단, 철자, 문법, 띄어쓰기, 가독성을 고려하여 작성해주세요. :

{text}
"""

custom_prompt_template = PromptTemplate(template=CUSTOM_PROMPT, input_variables=["text"])