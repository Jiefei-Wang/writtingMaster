
from modules.base_module import BaseModule
from dotenv import load_dotenv
from llm_output_parser import parse_json
from openai import OpenAI
from modules.settings import load_settings
from tqdm import tqdm
import multiprocessing as mp
import os
from modules.transition.worker import process_pair
load_dotenv()


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

        previous_contexts = []
        first_sentences = []
        second_sentences = []
        second_sentence_starts = []
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

                previous_contexts.append(previous_context)
                first_sentences.append(first_sentence['text'])
                second_sentences.append(second_sentence['text'])
                second_sentence_starts.append(second_sentence['start'])

        # Parallelize extraction across all collected sentence pairs with a progress bar
        tasks = list(zip(previous_contexts, first_sentences, second_sentences, second_sentence_starts))
        if tasks:
            proc_count = 10
            with mp.Pool(processes=proc_count) as pool, tqdm(total=len(tasks), desc="Transitions", unit="pair") as pbar:
                for res in pool.imap_unordered(process_pair, tasks, chunksize=1):
                    if res:
                        results.append(res)
                    pbar.update(1)

        results.sort(key=lambda x: x["start"])
        return {
            "module_name": self.name(),
            "results": results
        }
    