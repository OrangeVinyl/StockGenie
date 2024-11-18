import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 사전 학습된 감성 분석 모델과 토크나이저 로드
model_name = "beomi/kcbert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# 모델을 평가 모드로 설정
model.eval()

# GPU 사용 가능 시 GPU로 이동
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# 감성 분석할 문장들
sentences = [
    "이곳에서 보낸 휴가는 정말 잊지 못할 만큼 행복하고 즐거웠다. 아름다운 풍경과 사람들의 따뜻한 환대가 더해져 모든 순간이 마법 같았다.",
    "이번 경험은 정말 끔찍했다. 서비스는 엉망이었고, 모든 것이 계획된 것과 다르게 돌아가면서 실망만 안겨 주었다.",
    "회의는 그저 평범했다. 특별히 인상적인 부분은 없었지만, 그렇다고 불만을 가질 만한 요소도 없었다. 필요한 논의는 모두 이뤄진 것 같다."
]

# 라벨 매핑 (모델에 따라 다를 수 있습니다. 보통 긍정, 부정, 중립 등)
# 여기서는 예시로 세 가지 클래스로 가정합니다.
label_mapping = {0: 'negative', 1: 'neutral', 2: 'positive'}

# 감성 분석 수행
for sentence in sentences:
    # 입력 토크나이징
    inputs = tokenizer(sentence, return_tensors="pt", truncation=True, padding='max_length', max_length=128)
    inputs = {key: val.to(device) for key, val in inputs.items()}  # 입력 데이터를 GPU로 이동

    # 모델 예측
    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    probabilities = F.softmax(logits, dim=1)
    predicted_class = torch.argmax(probabilities, dim=1).item()
    confidence = probabilities[0][predicted_class].item()

    # 결과 출력
    print(f"문장: {sentence}")
    print(f"예측된 감정: {label_mapping.get(predicted_class, 'Unknown')} (신뢰도: {confidence:.4f})")
    print("-" * 50)