import kss
import re

def split_sentences(texts):
    """
    @description: 주어진 한글 텍스트를 문장 단위로 분리하여 반환
    현재, Mecab을 사용하여 문장을 분리하고 있음 > split_sentences attribute backend='Mecab'

    :param texts: list of str
    :return: list of str
    """
    sentences = []

    for text in texts:
        text = text.strip()
        for sentence in kss.split_sentences(text, backend='Mecab'):
            sentences.append(sentence.strip())

    return sentences


def split_sentences_en(texts):
    """
    @description: 주어진 영어 텍스트를 문장 단위로 분리하여 반환 (정규 표현식 사용)

    :param texts: list of str
    :return: list of str
    """
    sentences = []
    sentence_endings = re.compile(r'(?<=[.!?]) +')

    for text in texts:
        text = text.strip()
        split_sentence = sentence_endings.split(text)
        sentences.extend([sentence.strip() for sentence in split_sentence if sentence.strip()])

    return sentences