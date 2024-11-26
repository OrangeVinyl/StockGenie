from transformers import pipeline

pipe = pipeline(
    "text-classification",
    model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis",
    top_k=None
)

def predict_emotions_en(texts):
    """
    @description  여러 텍스트에 대한 감정 예측 함수. 각 문장별 결과와 전체 텍스트에 대한 종합 점수를 반환

    :param texts: list of strings
    :return: tuple (per_sentence_scores, aggregate_scores)
    """
    results = pipe(texts)

    per_sentence_scores = []
    for text, result in zip(texts, results):
        sentiment_scores = [
            {'label': item['label'], 'score': item['score']}
            for item in result
        ]
        per_sentence_scores.append({
            'sentiment_scores': sentiment_scores
        })

    # 종합 감성 점수 계산 (평균)
    aggregate_scores = {'negative': 0.0, 'neutral': 0.0, 'positive': 0.0}
    num_sentences = len(results)

    for result in results:
        for item in result:
            label = item['label']
            score = item['score']
            aggregate_scores[label] += score

    for label in aggregate_scores:
        aggregate_scores[label] /= num_sentences

    max_label = max(aggregate_scores, key=aggregate_scores.get)

    return per_sentence_scores, aggregate_scores, max_label



def test_en_sentiment():
    test_sentences = [
        "The company's stocks price increased by 5% after the announcement.",
        "There are concerns about the economic downturn affecting the market.",
        "New product launches have boosted investor confidence."
    ]

    per_sentence_scores_en, aggregate_scores_en, max_label = predict_emotions_en(test_sentences)

    # 영어 결과 출력
    print("===== English Sentiment Analysis =====")
    for item in per_sentence_scores_en:
        print(f"Text: {item['text']}")
        print(f"Sentiment Scores: {item['sentiment_scores']}\n")

    print("===== Aggregate English Sentiment Scores =====")
    print(
        f"Negative: {aggregate_scores_en['negative']:.4f}, Neutral: {aggregate_scores_en['neutral']:.4f}, Positive: {aggregate_scores_en['positive']:.4f}\n")