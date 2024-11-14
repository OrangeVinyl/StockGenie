import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("beomi/KcELECTRA-base")
model = AutoModelForSequenceClassification.from_pretrained("beomi/KcELECTRA-base", num_labels=3)

sentences = [
    "이곳에서 보낸 휴가는 정말 잊지 못할 만큼 행복하고 즐거웠다. 아름다운 풍경과 사람들의 따뜻한 환대가 더해져 모든 순간이 마법 같았다.",
    "이번 경험은 정말 끔찍했다. 서비스는 엉망이었고, 모든 것이 계획된 것과 다르게 돌아가면서 실망만 안겨 주었다.",
    "회의는 그저 평범했다. 특별히 인상적인 부분은 없었지만, 그렇다고 불만을 가질 만한 요소도 없었다. 필요한 논의는 모두 이뤄진 것 같다."
]


# 전처리된 단어 리스트 예제
processed_sentences = [
    ['휴가', '정말', '행복'],
    ['풍경', '사람', '환대', '순간', '마법', '같']
]

# # 문장에 대해 감성 분석
# for sentence in sentences:
#
#     # 입력 데이터 준비
#     inputs = tokenizer(sentence, return_tensors="pt")
#     outputs = model(**inputs)
#     logits = outputs.logits
#
#     # softmax를 사용해 확률 계산
#     probabilities = F.softmax(logits, dim=1)
#     predicted_class = torch.argmax(probabilities, dim=1).item()
#
#     # 클래스 매핑
#     labels = ["부정", "중립", "긍정"]
#     print(f"문장: {sentence}")
#     print(f"예측된 감성: {labels[predicted_class]}")
#     print(f"확률: {probabilities}\n")


for words in processed_sentences:
    # 단어 리스트를 문장으로 변환
    sentence = " ".join(words)

    # 입력 데이터 준비
    inputs = tokenizer(sentence, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits

    # softmax를 사용해 확률 계산
    probabilities = F.softmax(logits, dim=1)
    predicted_class = torch.argmax(probabilities, dim=1).item()

    # 클래스 매핑
    labels = ["부정", "중립", "긍정"]
    print(f"문장: {sentence}")
    print(f"예측된 감성: {labels[predicted_class]}")
    print(f"확률: {probabilities}\n")


# 긍정 : "이곳에서 보낸 휴가는 정말 잊지 못할 만큼 행복하고 즐거웠다. 아름다운 풍경과 사람들의 따뜻한 환대가 더해져 모든 순간이 마법 같았다."
# 부정 : "이 영화는 정말 최악이었다. 배우들의 연기력도 별로고, 스토리도 전혀 흥미롭지 않았다. 시간이 너무 아까웠다."
# 중립 : "이 제품은 가격 대비 성능이 괜찮은 편이다. 다만 디자인이 조금 더 다양했으면 좋겠다는 생각이 든다."