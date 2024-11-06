import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
query = 'ChatGPT는 어디에 활용될 수 있나요?'
message = [{'role': 'user', 'content': query}]
completion = client.chat.completions.create(model='gpt-3.5-turbo', messages=message)
response_text = completion.choices[0].message.content

print(response_text)