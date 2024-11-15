import pandas as pd
import chardet

"""
@description: 7가지 감정을 3가지로 변환하는 필터링 함수 | 일회성 코드
"""
def map_emotion(emotion):
    if emotion in ['happiness', 'surprise']:
        return 'positive'
    elif emotion == 'neutral':
        return 'neutral'
    elif emotion in ['angry', 'disgust', 'fear', 'sadness']:
        return 'negative'
    else:
        return 'unknown'

with open('../data/rating_.csv', 'rb') as f:
    result = chardet.detect(f.read())
    print(result)
encoding = result['encoding']

df = pd.read_csv('../data/rating_.csv', encoding='CP949')
df['label'] = df['situation'].apply(map_emotion)
print(df.head())

df.to_csv('../data/mapped_emotion_dataset.csv', index=False, encoding='UTF-8')

df = pd.read_csv('../data/mapped_emotion_dataset.csv', encoding='UTF-8')
first_row_words = df.loc[0, 'words']
print(first_row_words)

