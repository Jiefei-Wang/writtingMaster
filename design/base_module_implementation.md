# Base Module Implementation

## File: modules/base_module.py

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

This abstract base class defines the interface that all modules must implement:

1. `name()` - Returns a unique identifier for the module
2. `description()` - Returns a human-readable description of what the module does
3. `process(text)` - Processes text and returns results in the standardized format

All modules must inherit from this class and implement these three methods to ensure consistency across the application.