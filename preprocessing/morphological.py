"""
한국어 형태소 분석을 위한 함수들을 정의한 파일
Mecab을 사용하는 경우에만 주석을 해제하고 사용하면 됨

단, Mecab을 사용하기 위해서는 JDK 1.8 이상이 설치되어 있어야 함
"""

# from konlpy.tag import Mecab
#
# def load_stopwords(filepath):
#     with open(filepath, 'r', encoding='utf-8') as file:
#         stopwords = set(file.read().splitlines())
#     return stopwords
#
# def extract_relevant_words(text):
#     """
#     @description: 해당 텍스트에서 명사, 형용사, 부사 등의 품사만 추출하여 반환
#
#     :param text:
#     :return:
#     """
#     mecab = Mecab(dicpath=r"C:\mecab\share\mecab-kor-dic")
#     STOPWORDS = load_stopwords('../../data/stopwords.txt')
#
#     morphs = mecab.pos(text)
#
#     relevant_pos = ['NNG', 'NNP', 'VA', 'VX', 'VXA', 'MAG', 'MAJ']  # 일반 명사, 고유 명사, 형용사, 보조 용언, 일반 부사, 접속 부사
#     filtered_words = [word for word, pos in morphs if pos in relevant_pos]
#
#     cleaned_words = [word for word in filtered_words if word not in STOPWORDS]
#
#     return cleaned_words
