from modules.base_module import BaseModule
import re

class IsolatedPronounsModule(BaseModule):
    def name(self) -> str:
        return "isolated_pronouns"
    
    def description(self) -> str:
        return "Identifies isolated pronouns that don't carry specific meaning by themselves"
    
    def process(self, text: str) -> dict:
        pronouns = [
            "this",
            "that",
            "these",
            "those",
            "it",
            "they",
            "them"
        ]
        results = []
        for pronoun in pronouns:
            pattern = r'\b' + re.escape(pronoun) + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                results.append({
                    "start": match.start(),
                    "end": match.end(),
                    "explanation": "isolated pronoun"
                })
        results.sort(key=lambda x: x["start"])
        return {
            "module_name": self.name(),
            "results": results
        }