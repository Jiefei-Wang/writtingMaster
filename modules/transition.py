from modules.base_module import BaseModule
import re
import json
import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

class TransitionModule(BaseModule):
    def name(self) -> str:
        return "transition"
    
    def description(self) -> str:
        return "Identifies missing transition words between consecutive sentences within the same paragraph"
    
    def process(self, text: str) -> dict:
        # Load configuration
        config = self._load_config()
        load_dotenv()  # Load environment variables
        
        # Split text into paragraphs
        paragraphs = self._split_into_paragraphs(text)
        
        results = []
        
        # Process each paragraph
        for para_idx, paragraph in enumerate(paragraphs):
            # Split paragraph into sentences (simply by period for now)
            sentences = self._split_into_sentences(paragraph)
            
            # Process consecutive sentence pairs
            for i in range(len(sentences) - 1):
                first_sentence = sentences[i].strip()
                second_sentence = sentences[i + 1].strip()
                
                if not first_sentence or not second_sentence:
                    continue
                
                # Get previous context (up to 100 words)
                previous_context = self._get_previous_context(paragraphs, para_idx, i, first_sentence)
                
                # Check for transition words using LLM
                transition_result = self._check_transition(
                    first_sentence, 
                    second_sentence, 
                    previous_context,
                    config
                )
                
                if transition_result and transition_result.get("transition", 0) == 1:
                    candidates = transition_result.get("candidate", [])
                    if candidates:
                        # Find position of the second sentence in the original text
                        position = text.find(second_sentence)
                        if position != -1:
                            # Get the first word of the second sentence for highlighting
                            first_word_match = re.search(r'\b\w+\b', second_sentence)
                            if first_word_match:
                                first_word = first_word_match.group()
                                # Create the highlighted span with the first candidate
                                suggested_word = candidates[0]
                                span = f"***{suggested_word}*** {first_word}"
                                
                                results.append({
                                    "text_span": span,
                                    "position": position,
                                    "explanation": f"Lack of transition, needs word: {suggested_word}. Potential candidates: {', '.join(candidates)}"
                                })
        
        # Sort results by position
        results.sort(key=lambda x: x["position"])
        
        return {
            "module_name": self.name(),
            "module_description": self.description(),
            "results": results
        }
    
    def _load_config(self) -> dict:
        """Load configuration from settings.json"""
        try:
            with open("settings.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default configuration
            return {
                "llm_service": {
                    "service": "ollama",
                    "host": "localhost",
                    "port": 11434,
                    "model": "gemma3:4b"
                }
            }
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs based on double newlines"""
        return [p.strip() for p in text.split('\n\n') if p.strip()]
    
    def _split_into_sentences(self, paragraph: str) -> List[str]:
        """Split paragraph into sentences based on periods"""
        # Simple sentence splitting by period
        sentences = paragraph.split('.')
        # Re-add the period to each sentence except the last one
        result = []
        for i, sentence in enumerate(sentences):
            if i < len(sentences) - 1:  # Not the last sentence
                result.append(sentence.strip() + '.')
            else:  # Last sentence (might be empty)
                if sentence.strip():
                    result.append(sentence.strip())
        return result
    
    def _get_previous_context(self, paragraphs: List[str], para_idx: int, sent_idx: int, current_sentence: str) -> str:
        """Get previous context (up to 100 words) for the LLM prompt"""
        if para_idx == 0 and sent_idx == 0:
            return ""
        
        # Get previous sentences from the same paragraph
        if sent_idx > 0:
            # Get previous sentences in the same paragraph
            prev_context = " ".join([s for s in paragraphs[para_idx].split('.')[:sent_idx] if s.strip()])
        else:
            # Get last few sentences from previous paragraph
            prev_paragraph = paragraphs[para_idx - 1]
            prev_sentences = self._split_into_sentences(prev_paragraph)
            prev_context = " ".join(prev_sentences[-2:])  # Last 2 sentences
        
        # Limit to 100 words
        words = prev_context.split()
        if len(words) > 100:
            return " ".join(words[-100:])
        return prev_context
    
    def _check_transition(self, first_sentence: str, second_sentence: str, previous_context: str, config: dict) -> Dict[str, Any]:
        """Check if transition is needed between two sentences using LLM"""
        service_config = config.get("llm_service", {})
        service = service_config.get("service", "ollama")
        
        if service == "ollama":
            return self._check_transition_ollama(first_sentence, second_sentence, previous_context, service_config)
        elif service == "openai":
            return self._check_transition_openai(first_sentence, second_sentence, previous_context, service_config)
        else:
            # Default to ollama if service not recognized
            return self._check_transition_ollama(first_sentence, second_sentence, previous_context, service_config)
    
    def _check_transition_ollama(self, first_sentence: str, second_sentence: str, previous_context: str, config: dict) -> Dict[str, Any]:
        """Check transition using Ollama API"""
        host = config.get("host", "localhost")
        port = config.get("port", 11434)
        model = config.get("model", "gemma3:4b")
        
        # Load prompt template
        try:
            with open("modules/transition_prompt.txt", "r") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            # Fallback prompt
            prompt_template = """
You are an expert writing assistant specializing in identifying and suggesting transition words between sentences.

Analyze the following two consecutive sentences and determine if they require a transition word between them.

Previous context (for reference only):
{previous_context}

Sentence 1: "{sentence1}"
Sentence 2: "{sentence2}"

Instructions:
1. Determine if there is a proper transition word or phrase connecting these sentences
2. If there is no transition word, suggest appropriate candidates based on the relationship between the sentences
3. If there is already a transition word, respond with transition: 0

Response Format:
Respond ONLY with a JSON object in this exact format:
{
  "transition": 0 or 1,
  "candidate": ["candidate1", "candidate2", ...] or []
}
"""
        
        prompt = prompt_template.format(
            previous_context=previous_context,
            sentence1=first_sentence,
            sentence2=second_sentence
        )
        
        url = f"http://{host}:{port}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Parse the response
            response_text = result.get("response", "").strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group())
                    return json_data
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON response: {e}")
                    return {"transition": 0, "candidate": []}
            
            return {"transition": 0, "candidate": []}
            
        except requests.RequestException as e:
            print(f"Error calling Ollama API: {e}")
            return {"transition": 0, "candidate": []}
    
    def _check_transition_openai(self, first_sentence: str, second_sentence: str, previous_context: str, config: dict) -> Dict[str, Any]:
        """Check transition using OpenAI API"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("OpenAI API key not found in environment variables")
            return {"transition": 0, "candidate": []}
        
        model = config.get("model", "gpt-3.5-turbo")
        url = "https://api.openai.com/v1/chat/completions"
        
        # Load prompt template
        try:
            with open("modules/transition_prompt.txt", "r") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            # Fallback prompt
            prompt_template = """
You are an expert writing assistant specializing in identifying and suggesting transition words between sentences.

Analyze the following two consecutive sentences and determine if they require a transition word between them.

Previous context (for reference only):
{previous_context}

Sentence 1: "{sentence1}"
Sentence 2: "{sentence2}"

Instructions:
1. Determine if there is a proper transition word or phrase connecting these sentences
2. If there is no transition word, suggest appropriate candidates based on the relationship between the sentences
3. If there is already a transition word, respond with transition: 0

Response Format:
Respond ONLY with a JSON object in this exact format:
{
  "transition": 0 or 1,
  "candidate": ["candidate1", "candidate2", ...] or []
}
"""
        
        prompt = prompt_template.format(
            previous_context=previous_context,
            sentence1=first_sentence,
            sentence2=second_sentence
        )
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an expert writing assistant specializing in identifying and suggesting transition words between sentences."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Parse the response
            response_text = result["choices"][0]["message"]["content"].strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group())
                    return json_data
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON response: {e}")
                    return {"transition": 0, "candidate": []}
            
            return {"transition": 0, "candidate": []}
            
        except requests.RequestException as e:
            print(f"Error calling OpenAI API: {e}")
            return {"transition": 0, "candidate": []}