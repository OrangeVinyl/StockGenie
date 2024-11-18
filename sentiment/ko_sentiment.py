import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

model_save_path = '../models/kobert_emotion_classifier'
tokenizer = AutoTokenizer.from_pretrained(model_save_path)
model = AutoModelForSequenceClassification.from_pretrained(model_save_path)

def preprocess_text(text, tokenizer, max_length=128):
    """
    @description 텍스트 토크나이징 및 패딩

    :param text:
    :param tokenizer:
    :param max_length:
    :return: tokenized text
    """
    encoding = tokenizer(
        text,
        truncation=True,
        padding='max_length',
        max_length=max_length,
        return_tensors='pt'
    )
    return encoding

def predict_emotion(text, model, tokenizer):
    """
    @description 감정 예측 함수

    :param text:
    :param model:
    :param tokenizer:
    :return: Object
    """
    model.eval()  # 평가 모드로 전환
    encoding = preprocess_text(text, tokenizer)

    # 입력 데이터를 모델에 전달
    with torch.no_grad():
        outputs = model(**{key: val.to(model.device) for key, val in encoding.items()})

    # logits 가져오기
    logits = outputs.logits
    probs = F.softmax(logits, dim=1)  # 소프트맥스를 사용해 확률 계산
    predicted_label = torch.argmax(probs, dim=1).item()

    # 레이블을 원래 감정으로 매핑
    label_mapping = {0: 'negative', 1: 'neutral', 2: 'positive'}
    emotion = label_mapping[predicted_label]

    probs_list = probs.squeeze().tolist()

    # 확률 및 예측 결과 출력
    print("===== 예측 결과 =====")
    print(f"입력 문장: {text}")
    print("Logits(비정규화 점수): ", [round(logit, 4) for logit in logits.squeeze().tolist()])
    print("확률(%) : ", [round(prob * 100, 2) for prob in probs_list])
    print(f"예측 감성: {emotion}")
    print("=====================\n")

test_sentences = [
    "이곳에서 보낸 휴가는 정말 잊지 못할 만큼 행복하고 즐거웠다.",
    "이번 경험은 정말 끔찍했다. 서비스는 엉망이었고, 모든 것이 계획과 달랐다.",
    "회의는 평범했다. 특별히 인상적이지도, 불만스럽지도 않았다.",
    "오늘의 경험은 정말로 놀라웠어! 모든 게 완벽했고, 앞으로 다시 오고 싶어.",
    "이번 프로젝트는 매우 성공적이었어. 팀원 모두가 최선을 다해 협력했어.",
    "그 영화는 감동적이었고, 끝까지 눈을 뗄 수가 없었어.",
    "맛있는 음식을 먹고 좋은 사람들과 함께한 시간이 정말 소중했어.",
    "새로운 취미를 시작했는데 너무 재미있어서 시간이 어떻게 갔는지 몰랐어.",
    "서비스가 최악이었어. 두 번 다시 이용하고 싶지 않아.",
    "오늘 하루는 정말 최악이었어. 계획이 모두 엉망이 되었어.",
    "그 가게에서 산 물건이 금방 고장 나서 너무 실망스러웠어.",
    "지루하고 따분한 강의를 들어서 시간이 너무 더디게 갔어.",
    "음식이 차갑고 맛이 없어서 먹을 가치도 없었어.",
    "오늘의 날씨는 흐림이었다. 특별히 좋지도 나쁘지도 않았어.",
    "회의는 예정된 시간에 시작해서 필요한 내용을 논의하고 마쳤어.",
    "그는 가방을 들고 집을 나섰다. 별다른 사건은 없었어.",
    "점심으로 먹은 음식은 그냥 평범한 맛이었다.",
    "버스를 타고 목적지에 도착했어. 늦지도 일찍 도착하지도 않았어."
]

for sentence in test_sentences:
    predict_emotion(sentence, model, tokenizer)
