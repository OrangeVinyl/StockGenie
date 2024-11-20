from pykospacing import Spacing

def correct_spacing(sentences):
    """
    @description: 띄어쓰기를 교정하여 반환

    :param sentences: 
    :return: corrected_sentences
    """
    spacing = Spacing()
    corrected_sentences = [spacing(sentence) for sentence in sentences]
    return corrected_sentences
