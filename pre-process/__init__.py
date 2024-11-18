from ko.spacing import correct_spacing
from ko.splitter import split_sentences
from soynlp.normalizer import repeat_normalize
from cleaner import clean_punc, clean_text, punct, punct_mapping

def preprocess_ko(lines):
    normalized_lines = [repeat_normalize(line, num_repeats=2) for line in lines]

    spaced_lines = correct_spacing(normalized_lines)
    s_sentences = split_sentences(spaced_lines)
    clean_sentences = clean_text(s_sentences)

    ## 형태소 분석 -- ML/DL 모델에 따라 사용
    # processed_sentences = [extract_relevant_words(sentence) for sentence in clean_sentences]
    # print("Processed Sentences:", processed_sentences)

    return clean_sentences

def preprocess_en(lines):
    cleaned_lines = [clean_punc(line, punct, punct_mapping) for line in lines]
    cleaned_lines = [clean_text([line])[0] for line in cleaned_lines]
    return cleaned_lines


if __name__ == "__main__":

    sentences = [
        "이 영화는 정말 최악이었다. 배우들의 연기력도 별로고, 스토리도 전혀 흥미롭지 않았다. 시간이 너무 아까웠다.",
        "이 영화는 정말 최고였다. 배우들의 연기력도 좋았고, 스토리도 흥미로웠다. 시간이 너무 아깝지 않았다."
    ]

    en_sentences = [
        "I absolutely loved the new movie! It was fantastic and thrilling.",
        "The service was terrible. I had a very bad experience.",
        "The event was okay, nothing special but not bad either.",
        "I'm extremely happy with the results of this project.",
        "I'm disappointed with the quality of the product."
    ]

    processed = preprocess_ko(sentences)
    for tokens in processed:
        print(tokens)

    processed_en = preprocess_en(en_sentences)
    for cleaned in processed_en:
        print(cleaned)
