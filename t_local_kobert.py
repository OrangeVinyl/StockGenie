import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("kykim/bert-kor-base", trust_remote_code=True)
model = AutoModelForSequenceClassification.from_pretrained("kykim/bert-kor-base")

sentences = [
    "이곳에서 보낸 휴가는 정말 잊지 못할 만큼 행복하고 즐거웠다. 아름다운 풍경과 사람들의 따뜻한 환대가 더해져 모든 순간이 마법 같았다.",
    "이번 경험은 정말 끔찍했다. 서비스는 엉망이었고, 모든 것이 계획된 것과 다르게 돌아가면서 실망만 안겨 주었다.",
    "회의는 그저 평범했다. 특별히 인상적인 부분은 없었지만, 그렇다고 불만을 가질 만한 요소도 없었다. 필요한 논의는 모두 이뤄진 것 같다."
]


for sentence in sentences:

    inputs = tokenizer(sentence, return_tensors="pt")
    outputs = model(**inputs)

    logits = outputs.logits

    print(logits)

