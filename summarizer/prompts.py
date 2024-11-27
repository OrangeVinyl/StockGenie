CUSTOM_PROMPT ="""다음은 뉴스 기사입니다. 기사의 주요 내용을 기반으로 세 문장을 작성하세요. 
문장은 감정(긍정, 중립, 부정)이 드러나도록 요약하되, 기사의 흐름과 맥락을 왜곡하지 마세요. 
순서화 시키지 말고 자연스럽게 문장을 작성해주세요.
철자, 문법, 띄어쓰기, 가독성을 고려하여 작성해주세요. :

{text}
"""

EN_CUSTOM_PROMPT ="""Please read the following text and summarize its main points in English in three important sentences.
Please summarize the sentences so that emotions (positive, neutral, negative) are evident without distorting the flow and context of the article. 
Write the sentences naturally without ordering them.
Please consider spelling, grammar, spacing, and readability. :

{text}
"""