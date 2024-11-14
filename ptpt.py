import pandas as pd

# 데이터셋 불러오기 (예: CSV 형식)
df = pd.read_csv("../data/rating_data.csv", encoding = "utf-8")

# 7가지 감정을 3가지 범주로 매핑하는 함수
def map_emotion(emotion):
    if emotion in ['happiness', 'surprise']:
        return 'positive'
    elif emotion == 'neutral':
        return 'neutral'
    elif emotion in ['angry', 'disgust', 'fear', 'sadness']:
        return 'negative'

# '상황' 컬럼을 변환하여 새로운 '라벨' 컬럼 생성
df['라벨'] = df['상황'].apply(map_emotion)

# 새로운 데이터 확인
print(df.head())

# 변환된 데이터셋을 저장
df.to_csv("mapped_emotion_dataset.csv", index=False)
