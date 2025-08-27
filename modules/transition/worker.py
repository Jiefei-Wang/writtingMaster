
from modules.settings import load_settings
from llm_output_parser import parse_json
from modules.llm_adapter import chat_llm



def get_prompt(context, sentence1, sentence2):
    with open("modules/transition/prompt.txt") as f:
        prompt_template = f.read()
    prompt = prompt_template.replace(
            "{previous_context}", context
            ).replace(
                "{sentence1}", sentence1
            ).replace(
                "{sentence2}", sentence2
            )
    return prompt


def extract(context, sentence1, sentence2):
    prompt = get_prompt(context, sentence1, sentence2)

    messages=[
            {"role": "developer", "content": "Extract the information based on user's instruction"},
            {
                "role": "user",
                "content": prompt,
            },
        ]

    content = chat_llm(messages)
    try:
        data = parse_json(content)
    except Exception as e:
        print(f"Failed to parse LLM output: {e}")
        data = {}
    return data

def process_pair(args):
    previous_context, s1_text, s2_text, s2_start = args
    try:
        extraction_result = extract(previous_context, s1_text, s2_text)
        transition = int(extraction_result.get("transition", 0)) if isinstance(extraction_result, dict) else 0
        candidates = extraction_result.get("candidates", "") if isinstance(extraction_result, dict) else ""
        if transition == 0 or candidates == "":
            return None
        words = s2_text.split()
        if not words:
            return None
        first_word = words[0]
        start = s2_start
        end = start + len(first_word)
        return {
            "start": start,
            "end": end,
            "explanation": f"Lack of transition, Potential candidates: {candidates}",
        }
    except Exception as e:
        print(f"Error processing sentence pair: {e}")
        return None
