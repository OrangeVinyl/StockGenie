CUSTOM_PROMPT ="""다음은 뉴스 기사입니다. 기사의 주요 내용을 기반으로 세 문장을 작성하세요. 
각 문장은 감정(긍정, 중립, 부정)이 드러나도록 요약하되, 기사의 흐름과 맥락을 왜곡하지 마세요. 
각각의 문장은 하나의 핵심 메시지를 전달합니다.
순서화 시키지 말고 자연스럽게 문장을 작성해주세요.
철자, 문법, 띄어쓰기, 가독성을 고려하여 작성해주세요. :

{text}
"""

EN_CUSTOM_PROMPT ="""The following is a news article. 
Based on the main content of the article, please write three sentences. 
Each sentence should be a summary that conveys an emotion (positive, neutral, negative) without distorting the flow and context of the article. 
Each sentence should convey one core message. 
Do not order them; write the sentences naturally. Please consider spelling, grammar, spacing, and readability when writing. :

{text}
"""