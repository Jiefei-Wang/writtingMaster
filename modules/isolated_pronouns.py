from modules.base_module import BaseModule
import re

class IsolatedPronounsModule(BaseModule):
    def name(self) -> str:
        return "isolated_pronouns"
    
    def description(self) -> str:
        return "Identifies isolated pronouns that don't carry specific meaning by themselves"
    
    def process(self, text: str) -> dict:
        # Define isolated pronouns to match
        pronouns = ["this", "that", "these", "those"]
        results = []
        
        # Find all pronouns in the text
        for pronoun in pronouns:
            # Use word boundaries to match whole words only
            pattern = r'\b' + re.escape(pronoun) + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                results.append({
                    "text_span": match.group(),
                    "position": match.start(),
                    "explanation": "isolated pronoun"
                })
        
        # Sort results by position
        results.sort(key=lambda x: x["position"])
        
        return {
            "module_name": self.name(),
            "module_description": self.description(),
            "results": results
        }