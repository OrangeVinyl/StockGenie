from ko.splitter import split_sentences
from cleaner import clean_text
from ko.spacing import correct_spacing
from soynlp.normalizer import repeat_normalize

def preprocess_ko(lines):
    normalized_lines = [repeat_normalize(line, num_repeats=2) for line in lines]

    spaced_lines = correct_spacing(normalized_lines)
    s_sentences = split_sentences(spaced_lines)
    clean_sentences = clean_text(s_sentences)

    ## 형태소 분석 -- 머신러닝의 경우 사용
    # processed_sentences = [extract_relevant_words(sentence) for sentence in clean_sentences]
    # print("Processed Sentences:", processed_sentences)

    return clean_sentences


if __name__ == "__main__":

    sentences = [
        "이 영화는 정말 최악이었다. 배우들의 연기력도 별로고, 스토리도 전혀 흥미롭지 않았다. 시간이 너무 아까웠다."
    ]

    processed = preprocess_ko(sentences)
    for tokens in processed:
        print(tokens)
