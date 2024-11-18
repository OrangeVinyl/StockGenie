from transformers import pipeline

# pipe = pipeline("text-classification", model="ProsusAI/finbert")
pipe = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")

text = "The company's stock price increased by 5% after the announcement."

result = pipe(text)
print(result)