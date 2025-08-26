
from modules.base_module import BaseModule
from dotenv import load_dotenv
from llm_output_parser import parse_json
from openai import OpenAI
from modules.settings import load_settings
load_dotenv()


def get_prompts(contexts, sentence1s, sentence2s):
    prompts = []
    with open("modules/transition/prompt.txt") as f:
        prompt_template = f.read()
    for context, s1, s2 in zip(contexts, sentence1s, sentence2s):
        prompt = prompt_template.replace(
            "{previous_context}", context
            ).replace(
                "{sentence1}", s1
            ).replace(
                "{sentence2}", s2
            )
        prompts.append(prompt)
    return prompts

def extract(context, sentence1, sentence2):
    base_url = load_settings().get("llm_service", {}).get("base_url", None)
    client = OpenAI(
        base_url=base_url
    )
    prompts = get_prompts([context], [sentence1], [sentence2])
    prompt = prompts[0]

    completion = client.chat.completions.create(
        model = "gemma3:4b",
        messages=[
            {"role": "developer", "content": "Extract the information based on user's instruction"},
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    data = parse_json(completion.choices[0].message.content)
    return data

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





class TransitionModule(BaseModule):
    def name(self) -> str:
        return "transition"
    
    def description(self) -> str:
        return "Identifies missing transition words between consecutive sentences within the same paragraph"
    
    
    def process(self, text: str) -> dict:
        # Split text into paragraphs
        paragraphs = split_into_paragraphs(text)
        results = []

        for paragraph in paragraphs:
            paragraph_text = paragraph['text']
            start_paragraph = paragraph['start']
            sentences = split_into_sentences(paragraph)
            for i in range(len(sentences) - 1):
                first_sentence = sentences[i]
                second_sentence = sentences[i + 1]
                if i == 0:
                    previous_context = ""
                else:
                    previous_context = sentences[i - 1]['text']

                # Use Kor to extract
                try:
                    extraction_result = extract(previous_context, first_sentence['text'], second_sentence['text'])
                    transition = extraction_result.get("transition", 0)
                    candidates = extraction_result.get("candidates", '')
                    if int(transition) == 0 or candidates == '':
                        continue
                    else:
                        second_sentence_words = second_sentence['text'].split()
                        second_sentence_first_word = second_sentence_words[0] 
                        start = second_sentence['start']
                        end = start + len(second_sentence_first_word)
                        results.append({
                            "start": start,
                            "end": end,
                            "explanation": f"Lack of transition, Potential candidates: {candidates}"
                        })
                except Exception as e:
                    print(f"Error processing sentence pair: {e}")
                    continue

        results.sort(key=lambda x: x["start"])
        return {
            "module_name": self.name(),
            "results": results
        }
    