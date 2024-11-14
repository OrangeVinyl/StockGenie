from konlpy.tag import Mecab

def load_stopwords(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        stopwords = set(file.read().splitlines())
    return stopwords

def extract_relevant_words(text):
    """
    @description: 해당 텍스트에서 명사, 형용사, 부사 등의 품사만 추출하여 반환

    :param text:
    :return:
    """
    mecab = Mecab(dicpath=r"C:\mecab\share\mecab-ko-dic")
    STOPWORDS = load_stopwords('../data/stopwords.txt')

    morphs = mecab.pos(text)

    relevant_pos = ['NNG', 'NNP', 'VA', 'VX', 'VXA', 'MAG', 'MAJ']  # 일반 명사, 고유 명사, 형용사, 보조 용언, 일반 부사, 접속 부사
    filtered_words = [word for word, pos in morphs if pos in relevant_pos]

    cleaned_words = [word for word in filtered_words if word not in STOPWORDS]

    return cleaned_words
