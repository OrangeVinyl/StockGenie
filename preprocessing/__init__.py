import os
import json
from soynlp.normalizer import repeat_normalize
from preprocessing.spacing import correct_spacing
from preprocessing.splitter import split_sentences, split_sentences_en
from preprocessing.cleaner import clean_punc, clean_text, punct, punct_mapping


def preprocess_ko(lines):
    normalized_lines = [repeat_normalize(line, num_repeats=2) for line in lines]
    spaced_lines = correct_spacing(normalized_lines)
    splits = split_sentences(spaced_lines)
    clean_sentences = clean_text(splits)

    return clean_sentences

def preprocess_en(lines):
    clean_punc_lines = [clean_punc(line, punct, punct_mapping) for line in lines]
    splits = split_sentences_en(clean_punc_lines)
    clean_sentences = clean_text(splits)

    return clean_sentences


def preprocess_json(source, dir_path, company_name):
    """
    @description 지정된 디렉토리 내의 모든 JSON 파일을 읽고, 각 파일의 'summary' 필드를 전처리하여
    'pre_processed_summary' 키로 저장하는 함수

    :param source: str - '국내' 또는 '해외'
    :param dir_path: str - JSON 파일들이 저장된 디렉토리 경로
    :param company_name: str - 회사명
    """
    print("==============================[전처리]==============================")
    company_name_lower = company_name.lower()

    for filename in os.listdir(dir_path):
        if filename.lower().endswith('.json') and company_name_lower in filename.lower():
            file_path = os.path.join(dir_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Error decoding JSON from file {file_path}: {e}")
                    continue

            for entry in data:
                summary = entry.get('summary', '')
                if summary:
                    if source == '국내':
                        processed_summary = preprocess_ko([summary])
                    elif source == '해외':
                        processed_summary = preprocess_en([summary])
                    else:
                        processed_summary = summary

                    entry['pre_processed_summary'] = processed_summary
                else:
                    entry['pre_processed_summary'] = ''

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"[SUCCESS] 전처리 완료: {file_path}")


def test_preprocessing():
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

if __name__ == '__main__':
    test_preprocessing()