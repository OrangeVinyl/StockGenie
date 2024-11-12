import kss

def tokenize_text(lines):
    sentence_tokenized_text = []

    for i, line in enumerate(lines):
        line = line.strip()
        for sent in kss.split_sentences(line):
            sentence_tokenized_text.append(sent.strip())

    return sentence_tokenized_text