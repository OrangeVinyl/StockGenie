import torch
import warnings
import numpy as np
import pandas as pd
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments

"""
@description: 한국어 감정 분석 모델을 학습하는 스크립트

1. 데이터 로드
2. 라벨 인코딩
3. 데이터 분할
4. 토크나이저 로드
5. 데이터셋 클래스 정의
6. 데이터셋 생성
7. 모델 로드
8. 평가 지표 함수 정의
9. 훈련 인자 설정
10. Trainer 초기화
11. 모델 학습
12. 평가
13. 모델 저장
"""

warnings.filterwarnings("ignore", category=FutureWarning)

df = pd.read_csv('../data/mapped_emotion_dataset.csv', encoding='utf-8')

label_mapping = {'negative': 0, 'neutral': 1, 'positive': 2}
df['label'] = df['label'].map(label_mapping)

train_texts, test_texts, train_labels, test_labels = train_test_split(
    df['words'].tolist(),
    df['label'].tolist(),
    test_size=0.2,
    random_state=42,
    stratify=df['label']
)
tokenizer = AutoTokenizer.from_pretrained("kykim/bert-kor-base", trust_remote_code=True)

class EmotionDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )

        # 'input_ids'와 'attention_mask'는 tensor의 첫번째 요소를 추출
        item = {key: val.squeeze() for key, val in encoding.items()}
        item['labels'] = torch.tensor(label, dtype=torch.long)
        return item


train_dataset = EmotionDataset(train_texts, train_labels, tokenizer)
test_dataset = EmotionDataset(test_texts, test_labels, tokenizer)

model = AutoModelForSequenceClassification.from_pretrained(
    "kykim/bert-kor-base",
    num_labels=3,  # negative, neutral, positive
    # problem_type="multi_label_classification"
)

def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

training_args = TrainingArguments(
    output_dir='../results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='../logs',
    logging_steps=10,
    eval_strategy='epoch',
    save_strategy='epoch',
    load_best_model_at_end=True,
    metric_for_best_model='f1',
    greater_is_better=True
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    processing_class =tokenizer,
    compute_metrics=compute_metrics
)

trainer.train()

eval_results = trainer.evaluate()
print(f"Evaluation results: {eval_results}")

model_save_path = '../models/kobert_emotion_classifier'
trainer.save_model(model_save_path)
tokenizer.save_pretrained(model_save_path)