from langchain.prompts import PromptTemplate

CUSTOM_PROMPT ="""다음 텍스트를 읽고, 핵심 내용을 한국어로 5문장으로 요약해 주세요.
단, 철자, 문법, 띄어쓰기, 가독성을 고려하여 작성해주세요. :

{text}
"""

EN_CUSTOM_PROMPT ="""Please read the following text and summarize its main points in English in five sentences.
Please consider spelling, grammar, spacing, and readability. :

{text}
"""

custom_prompt_template = PromptTemplate(template=CUSTOM_PROMPT, input_variables=["text"])