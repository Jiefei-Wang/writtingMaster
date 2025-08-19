# Isolated Pronouns Module Design

## File: modules/isolated_pronouns.py

```python
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
```

## Module Functionality

This module identifies isolated pronouns in text that may not carry specific meaning by themselves. These include:

- "this" - often used without clear antecedent
- "that" - often used without clear antecedent
- "these" - often used without clear antecedent
- "those" - often used without clear antecedent

The module uses regular expressions with word boundaries to ensure it only matches complete words and not partial matches within other words.

## Result Format

For each match, the module returns:
- `text_span`: The actual pronoun found in the text
- `position`: The character position where the pronoun was found
- `explanation`: A simple explanation that it's an "isolated pronoun"

The results are sorted by position to maintain the order they appear in the text.