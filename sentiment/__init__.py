import os
import json
from sentiment.ko_sentiment import predict_emotions, tokenizer, model
from sentiment.en_sentiment import predict_emotions_en

def decide_sentiment(source, dir_path, company_name):
    company_name_lower = company_name.lower()

    for filename in os.listdir(dir_path):
        if filename.lower().endswith('.json') and company_name_lower in filename.lower():
            file_path = os.path.join(dir_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"[ERROR] JSON 파일 DECODING 실패 {file_path}: {e}")
                    continue

            for entry in data:
                pre_processed_summary = entry.get('pre_processed_summary', '')
                per_sentence_scores, aggregate_scores = [], []
                max_label = 'neutral'
                if pre_processed_summary:
                    if source == '국내':
                        per_sentence_scores, aggregate_scores, max_label = predict_emotions(pre_processed_summary, model, tokenizer)
                    elif source == '해외':
                        per_sentence_scores, aggregate_scores, max_label = predict_emotions_en(pre_processed_summary)

                    entry['per_sentence_scores'] = per_sentence_scores
                    entry['aggregate_scores'] = aggregate_scores
                    entry['emotion'] = max_label

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            print(f"[SUCCESS] 감성분석 완료: {file_path}")