import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

## 모델 및 토크나이저 불러오기(test_ko_sentiment 실행 시 주석 해제)
# model_save_path = '../models/kobert_emotion_classifier'
# tokenizer = AutoTokenizer.from_pretrained(model_save_path)
# model = AutoModelForSequenceClassification.from_pretrained(model_save_path)

def tokenizing_texts(texts, tokenizer, max_length=128):
    """
    @description 여러 텍스트를 토크나이징 및 패딩 후 토크나이저 출력 반환

    :param texts: list of strings
    :param tokenizer: HuggingFace tokenizer
    :param max_length: int - 최대 토큰 길이
    :return: 토크나이징된 텍스트
    """
    encoding = tokenizer(
        texts,
        truncation=True,
        padding=True,
        max_length=max_length,
        return_tensors='pt'
    )
    return encoding

def predict_emotions(texts, model, tokenizer):
    """
    @description 여러 텍스트에 대한 감정 예측 함수. 각 문장별 결과와 전체 텍스트에 대한 종합 점수를 반환

    :param texts: list of strings
    :param model: HuggingFace 모델
    :param tokenizer: HuggingFace 토크나이저
    :return: tuple (per_sentence_scores, aggregate_scores)
    """
    model.eval()
    encoding = tokenizing_texts(texts, tokenizer)

    with torch.no_grad():
        inputs = {key: val.to(model.device) for key, val in encoding.items()}
        outputs = model(**inputs)

    # logits 가져오기
    logits = outputs.logits
    probs = F.softmax(logits, dim=1)
    probs_list = probs.tolist()

    label_mapping = {0: 'negative', 1: 'neutral', 2: 'positive'}

    # 각 문장별 감정 점수
    per_sentence_scores = []
    for text, prob in zip(texts, probs_list):
        sentiment_scores = [
            {'label': label_mapping[i], 'score': prob[i]}
            for i in range(len(prob))
        ]
        per_sentence_scores.append({
            'sentiment_scores': sentiment_scores
        })

    # 전체 텍스트에 대한 종합 감정 점수 (평균)
    aggregate_scores = {'negative': 0.0, 'neutral': 0.0, 'positive': 0.0}
    for prob in probs_list:
        for i, score in enumerate(prob):
            aggregate_scores[label_mapping[i]] += score

    num_sentences = len(probs_list)
    for key in aggregate_scores:
        aggregate_scores[key] /= num_sentences

    return per_sentence_scores, aggregate_scores

# def test_ko_sentiment():
#     test_sentences = [
#         "이곳에서 보낸 휴가는 정말 잊지 못할 만큼 행복하고 즐거웠다.",
#         "이번 경험은 정말 끔찍했다. 서비스는 엉망이었고, 모든 것이 계획과 달랐다.",
#         "회의는 평범했다. 특별히 인상적이지도, 불만스럽지도 않았다.",
#         "오늘의 경험은 정말로 놀라웠어! 모든 게 완벽했고, 앞으로 다시 오고 싶어.",
#         "이번 프로젝트는 매우 성공적이었어. 팀원 모두가 최선을 다해 협력했어.",
#         "그 영화는 감동적이었고, 끝까지 눈을 뗄 수가 없었어.",
#         "맛있는 음식을 먹고 좋은 사람들과 함께한 시간이 정말 소중했어.",
#         "새로운 취미를 시작했는데 너무 재미있어서 시간이 어떻게 갔는지 몰랐어.",
#         "서비스가 최악이었어. 두 번 다시 이용하고 싶지 않아.",
#         "오늘 하루는 정말 최악이었어. 계획이 모두 엉망이 되었어.",
#         "그 가게에서 산 물건이 금방 고장 나서 너무 실망스러웠어.",
#         "지루하고 따분한 강의를 들어서 시간이 너무 더디게 갔어.",
#         "음식이 차갑고 맛이 없어서 먹을 가치도 없었어.",
#         "오늘의 날씨는 흐림이었다. 특별히 좋지도 나쁘지도 않았어.",
#         "회의는 예정된 시간에 시작해서 필요한 내용을 논의하고 마쳤어.",
#         "그는 가방을 들고 집을 나섰다. 별다른 사건은 없었어.",
#         "점심으로 먹은 음식은 그냥 평범한 맛이었다.",
#         "버스를 타고 목적지에 도착했어. 늦지도 일찍 도착하지도 않았어."
#     ]
#
#     per_sentence_scores, aggregate_scores = predict_emotions(test_sentences, model, tokenizer)
#
#     # 각 문장별 결과 출력
#     for item in per_sentence_scores:
#         print(f"Text: {item['text']}")
#         print(f"Sentiment Scores: {item['sentiment_scores']}\n")
#
#     # 종합 감정 점수 출력
#     print("===== [Aggregate Sentiment Scores] =====")
#     print(
#         f"Negative: {aggregate_scores['negative']:.4f}, Neutral: {aggregate_scores['neutral']:.4f}, Positive: {aggregate_scores['positive']:.4f}\n")


## TODO: 배치 처리 코드 추가
# def predict_emotions(texts, model, tokenizer, batch_size=8):
#     """
#     @description 감정 예측 함수 (배치 처리)
#
#     :param texts:
#     :param model:
#     :param tokenizer:
#     :param batch_size:
#     :return: None
#     """
#     model.eval()  # 모델을 평가 모드로 설정
#     device = next(model.parameters()).device
#
#     label_mapping = {0: 'negative', 1: 'neutral', 2: 'positive'}
#
#     for i in range(0, len(texts), batch_size):
#         batch_texts = texts[i:i+batch_size]
#         encoding = tokenizing_texts(batch_texts, tokenizer)
#         inputs = {key: val.to(device) for key, val in encoding.items()}
#
#         with torch.no_grad():
#             outputs = model(**inputs)
#
#         logits = outputs.logits
#         probs = F.softmax(logits, dim=1)
#         probs_list = probs.tolist()
#
#         for text, prob in zip(batch_texts, probs_list):
#             sentiment_scores = [
#                 {'label': label_mapping[j], 'score': round(prob[j], 4)}
#                 for j in range(len(prob))
#             ]
#             print(f"Text: {text}")
#             print(f"Sentiment Scores: {sentiment_scores}\n")