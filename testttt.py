import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")


url = 'https://newsapi.org/v2/everything'
params = {
        'q': 'BitCoin',
        'from': '2024-11-7',
        'to': '2024-11-18',
        'language': 'en',
        'page': 1,
        'sortBy': 'publishedAt',
        'apiKey': API_KEY
}

response = requests.get(url, params=params)
response.raise_for_status()

data = response.json()

print (data.get('totalResults'))
print(len(data.get('articles')))
print(data.get('articles'))

params2 = {
        'q': 'BitCoin',
        'from': '2024-11-7',
        'to': '2024-11-18',
        'language': 'en',
        'page': 2,
        'sortBy': 'publishedAt',
        'apiKey': API_KEY
}

res = requests.get(url, params=params2)
res.raise_for_status()

data = res.json()

print (data.get('totalResults'))
print(len(data.get('articles')))
print(data.get('articles'))
