
def offset_and_strip(text):
    s = text.lstrip()
    offset = len(text) - len(s)
    s = s.rstrip()
    return s, offset

def split_into_paragraphs(text: str):
    """Split text into paragraphs based on single newlines. Returns list of dicts with 'text' and 'start' (position in original text). Empty paragraphs are included if there are multiple newlines."""
    paragraphs = []
    idx = 0
    lines = text.split('\n')
    for line in lines:
        s, offset = offset_and_strip(line)
        if s!="":
            paragraphs.append({'text': s, 'start': idx + offset})
        idx += len(line) + 1  # +1 for the split '\n'
    return paragraphs

def split_into_sentences(paragraph: dict):
    """Split paragraph into sentences based on periods. Returns list of dicts with 'text' and 'start' (index in raw text)."""
    para_text = paragraph['text']
    para_start = paragraph['start']
    if para_text=='': 
        return []
    sentences = []
    idx = 0
    parts = para_text.split('.')
    for i, part in enumerate(parts):
        ## count how many spaces before the sentence and add to the start position
        s, offset = offset_and_strip(part)
        if s!="":
            sentences.append({'text': s, 'start': idx + para_start + offset})
        idx = idx + len(part) + 1
    return sentences