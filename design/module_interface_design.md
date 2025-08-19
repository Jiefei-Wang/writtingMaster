# Module Interface Design

## Abstract Base Class

All modules must inherit from the `BaseModule` abstract class and implement its required methods.

### BaseModule Class Definition

```python
from abc import ABC, abstractmethod

class BaseModule(ABC):
    @abstractmethod
    def name(self) -> str:
        """Return the name of the module (used for identification)"""
        pass
    
    @abstractmethod
    def description(self) -> str:
        """Return a description of what the module does"""
        pass
    
    @abstractmethod
    def process(self, text: str) -> dict:
        """
        Process the text and return results in standardized format
        
        Args:
            text (str): The text to process
            
        Returns:
            dict: Results in standardized format
            {
                "module_name": str,
                "module_description": str,
                "results": [
                    {
                        "text_span": str,
                        "position": int,
                        "explanation": str
                    }
                ]
            }
        """
        pass
```

## Module Implementation Requirements

Each module must:

1. Inherit from `BaseModule`
2. Implement all abstract methods:
   - `name()` - Returns a unique identifier for the module
   - `description()` - Returns a human-readable description of what the module does
   - `process(text)` - Processes text and returns results in the standardized format

3. Return results in the specified JSON format:
   ```json
   {
     "module_name": "module_identifier",
     "module_description": "Description of what this module does",
     "results": [
       {
         "text_span": "matched_text",
         "position": character_position_in_text,
         "explanation": "Markdown formatted explanation of why this was matched"
       }
     ]
   }
   ```

## Example Implementation (Isolated Pronouns Module)

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

## Module Discovery Mechanism

The main application will automatically discover modules by:

1. Scanning the `modules/` directory for Python files
2. Importing each module dynamically
3. Instantiating the module class
4. Registering it with a registry for later use

This allows users to simply drop a new module file in the `modules/` directory without modifying the main application code.