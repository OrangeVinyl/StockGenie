import kss

def split_sentences(texts):
    """
    @description: 주어진 텍스트를 문장 단위로 분리하여 반환

    :param texts:
    :return:
    """
    sentences = []

    for text in texts:
        text = text.strip()
        for sentence in kss.split_sentences(text):
            sentences.append(sentence.strip())

    return sentences