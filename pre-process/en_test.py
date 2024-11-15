from cleaner import clean_punc, clean_text, punct, punct_mapping

def preprocess_en(text):
    text = clean_punc(text, punct, punct_mapping)
    text = clean_text([text])[0]
    return text

en_sentences = [
    "I absolutely loved the new movie! It was fantastic and thrilling.",
    "The service was terrible. I had a very bad experience.",
    "The event was okay, nothing special but not bad either.",
    "I'm extremely happy with the results of this project.",
    "I'm disappointed with the quality of the product."
]

cleaned_sentences = [preprocess_en(sentence) for sentence in en_sentences]

for original, cleaned in zip(en_sentences, cleaned_sentences):
    print(f"Original: {original}")
    print(f"Cleaned: {cleaned}")
    print("-" * 50)