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
                "results": [
                    {
                        "start": int,
                        "end": int,
                        "explanation": str
                    }
                ]
            }
        """
        pass