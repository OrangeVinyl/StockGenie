import re

punct = "/-'?!.,#$%\'()*+-/:;<=>@[\\]^_`{|}~" + '""“”’' + '∞θ÷α•à−β∅³π‘₹´°£€\×™√²—–&'
punct_mapping = {"‘": "'", "₹": "e", "´": "'", "°": "", "€": "e", "™": "tm", "√": " sqrt ", "×": "x", "²": "2",
                 "—": "-", "–": "-", "’": "'", "_": "-", "`": "'", '“': '"', '”': '"', '“': '"', "£": "e",
                 '∞': 'infinity', 'θ': 'theta', '÷': '/', 'α': 'alpha', '•': '.', 'à': 'a', '−': '-', 'β': 'beta',
                 '∅': '', '³': '3', 'π': 'pi', }

def clean_punc(text, punct, mapping):
    """
    @description: 특수 문자를 정제하여 반환하는 함수

    :param text: string
    :param punct: array of punctuation
    :param mapping: array of mapping
    :return: string
    """
    for p in mapping:
        text = text.replace(p, mapping[p])

    for p in punct:
        text = text.replace(p, f' {p} ')

    specials = {'\u200b': ' ', '…': ' ... ', '\ufeff': '', 'करना': '', 'है': ''}
    for s in specials:
        text = text.replace(s, specials[s])

    return text.strip()

def clean_text(texts):
    """
    @description: 텍스트를 정제하여 반환하는 함수

    - 특수 문자 정제
    - 구두점 제거
    - 숫자 제거
    - 소문자 변환
    - 불필요한 공백 제거
    - HTML 태그 제거
    - 문자열 시작 부분의 공백 제거
    - 문자열 끝 부분의 공백 제거

    :param texts: string
    :return: Array
    """
    corpus = []
    for text in texts:

        lines = text.split('\n')
        clean_lines = []

        for line in lines:
            review = clean_punc(line, punct, punct_mapping)
            review = re.sub(r'[@%\\*=()/~#&\+á?\xc3\xa1\-\|\:\;\!\-\,\_\~\$\'\"]', '', review)
            review = re.sub(r'\d+', '', review)  # 숫자 제거
            review = review.lower()  # 소문자 변환
            review = re.sub(r'\s+', ' ', review)  # 불필요한 공백 제거
            review = re.sub(r'<[^>]+>', '', review)  # HTML 태그 제거
            review = re.sub(r'^\s+', '', review)  # 문자열 시작 부분의 공백 제거
            review = re.sub(r'\s+$', '', review)  # 문자열 끝 부분의 공백 제거
            clean_lines.append(review)

        # 정제된 줄들을 다시 개행 문자로 연결
        corpus.append("\n".join(clean_lines))
    return corpus