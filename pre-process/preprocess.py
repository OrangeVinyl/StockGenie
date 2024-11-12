from tokenizer import tokenize_text
from cleaner import clean_text
from spacing import correct_spacing
from soynlp.normalizer import repeat_normalize
from morphological import extract_relevant_words



def preprocess(lines):
    normalized_lines = [repeat_normalize(line, num_repeats=2) for line in lines]
    print("Normalized Lines:", normalized_lines)

    spaced_lines = correct_spacing(lines)
    print("Spaced Lines:", spaced_lines)

    tokenize_sentences = tokenize_text(spaced_lines)
    print("Tokenized Sentences:", tokenize_sentences)

    clean_sentences = clean_text(tokenize_sentences)
    print("Cleaned Sentences:", clean_sentences)

    processed_sentences = [extract_relevant_words(sentence) for sentence in clean_sentences]
    print("Processed Sentences:", processed_sentences)

    return processed_sentences


if __name__ == "__main__":
    # 예시 입력
    sample_lines = [
        "안녕하세요.이것은예시문장입니다! 도레미파솔라시이상하게뭔가각 말이 안된다 이게머중",
        "텍스트전처리를진행중입니다."
    ]

    processed = preprocess(sample_lines)
    for tokens in processed:
        print(tokens)
