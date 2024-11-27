import os
import spacy
from konlpy.tag import Okt

nlp_en = spacy.load('en_core_web_sm')
stopwords_en = nlp_en.Defaults.stop_words

def load_stopwords(filepath):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    stopwords_path = os.path.join(current_dir, filepath)

    with open(stopwords_path, 'r', encoding='utf-8') as file:
        stopwords = set(file.read().splitlines())

    return stopwords


def extract_relevant_words_ko(text):
    """
    @description 한국어 텍스트에서 명사, 형용사, 부사 등의 품사만 추출하여 반환하는 함수

    :param text: str - 입력 텍스트
    :return: List - 추출된 단어 리스트
    """
    STOPWORDS = load_stopwords('../data/stopwords.txt')

    okt = Okt()
    tokens = okt.pos(text)
    relevant_pos = ['Noun', 'Adjective', 'Adverb']  # 명사, 형용사, 부사
    filtered_words = [word for word, pos in tokens if pos in relevant_pos]
    cleaned_words = [word for word in filtered_words if word not in STOPWORDS]

    return cleaned_words


def extract_relevant_words_en(text):
    """
    @description: 해당 텍스트에서 명사, 형용사, 부사 등의 품사만 추출하여 반환하는 함수 using spaCy

    :param text: str - 입력 텍스트
    :return: List - 추출된 단어 리스트
    """
    doc = nlp_en(text)
    relevant_pos = {'NOUN', 'ADJ', 'ADV'}  # 명사, 형용사, 부사
    cleaned_words = [
        token.text for token in doc
        if token.pos_ in relevant_pos and token.text.lower() not in stopwords_en and token.is_alpha
    ]
    return cleaned_words


def test_morphological_analysis():
    text = "아버지가 방에 들어가신다."
    print(extract_relevant_words_ko(text))  # ['아버지', '방', '들어가다']

    text_en = "The quick brown fox jumps over the lazy dog."
    print("English:", extract_relevant_words_en(text_en))


# def extract_relevant_words_mecab(text):
#     """
#     @description: 해당 텍스트에서 명사, 형용사, 부사 등의 품사만 추출하여 반환
#
#     Mecab을 사용하는 경우에만 주석을 해제하고 사용하면 됨
#     단, Mecab을 사용하기 위해서는 JDK 1.8 이상이 설치되어 있어야 함
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