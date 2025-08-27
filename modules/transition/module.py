
from dotenv import load_dotenv

from modules.logger import module_logger

from modules.base_module import BaseModule
from llm_output_parser import parse_json
from modules.sentence_splitter import split_into_paragraphs, split_into_sentences
from modules.llm_adapter import batch_chat_llm
load_dotenv()


def get_messages(context, sentence1, sentence2):
    with open("modules/transition/prompt.txt") as f:
        prompt_template = f.read()
    prompt = prompt_template.replace(
            "{previous_context}", context
            ).replace(
                "{sentence1}", sentence1
            ).replace(
                "{sentence2}", sentence2
            )
    
    messages=[
            {"role": "developer", "content": "Extract the information based on user's instruction"},
            {
                "role": "user",
                "content": prompt,
            },
        ]
    return messages


def extract_json(messages_list):
    content_list = batch_chat_llm(messages_list)
    data_list = []
    for content in content_list:
        try:
            data = parse_json(content)
        except Exception as e:
            print(f"Failed to parse LLM output: {e}")
            data = {}
        data_list.append(data)
    return data_list



class TransitionModule(BaseModule):
    def name(self) -> str:
        return "transition"
    
    def description(self) -> str:
        return "Identifies missing transition words between consecutive sentences within the same paragraph"
    
    
    def process(self, text: str) -> dict:
        # Split text into paragraphs
        paragraphs = split_into_paragraphs(text)
        results = []

        ## prepare the sentences for llm prompt
        previous_contexts = []
        first_sentences = []
        second_sentences = []
        second_sentence_starts = []
        for paragraph in paragraphs:
            sentences = split_into_sentences(paragraph)
            for i in range(len(sentences) - 1):
                first_sentence = sentences[i]
                second_sentence = sentences[i + 1]
                if i == 0:
                    previous_context = ""
                else:
                    previous_context = sentences[i - 1]['text']

                previous_contexts.append(previous_context)
                first_sentences.append(first_sentence['text'])
                second_sentences.append(second_sentence['text'])
                second_sentence_starts.append(second_sentence['start'])

        # get prompts and send to llm for data extraction
        # return json
        messages_list = [get_messages(ctx, s1, s2) for ctx, s1, s2 in zip(previous_contexts, first_sentences, second_sentences)]
        
        module_logger.info(f"Transition: Sending {len(messages_list)} messages to LLM")
        json_list = extract_json(messages_list)

        results = []
        for json_result, s2_text, s2_start in zip(json_list, second_sentences, second_sentence_starts):
            transition = int(json_result.get("transition", 0)) if isinstance(json_result, dict) else 0
            candidates = json_result.get("candidates", "") if isinstance(json_result, dict) else ""
            if transition == 0 or candidates == "":
                continue
            words = s2_text.split()
            if not words:
                continue
            first_word = words[0]
            start = s2_start
            end = start + len(first_word)
            results.append({
                "start": start,
                "end": end,
                "explanation": f"Lack of transition, Potential candidates: {candidates}",
            })
            
        module_logger.info(f"Transition: Obtained {len(results)} results")

        
        
        results.sort(key=lambda x: x["start"])
        return {
            "module_name": self.name(),
            "results": results
        }
    