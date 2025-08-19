#!/usr/bin/env python3
"""
Test script for the transition module
"""

def test_transition_module():
    """Test the transition module with sample text"""
    import sys
    import os
    import json
    
    # Add the current directory to the path so we can import modules
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from modules.transition import TransitionModule
        
        module = TransitionModule()
        
        # Sample text with missing transitions
        sample_text = """Research should promising result.
we still do not understand its mechanism

The weather was beautiful.
it started raining in the afternoon.

The experiment succeeded.
The results were inconclusive.

First, we conducted the survey.
we analyzed the data.
"""
        
        print("Testing transition module...")
        print(f"Module name: {module.name()}")
        print(f"Module description: {module.description()}")
        print()
        
        # Process the text
        results = module.process(sample_text)
        
        print("Results:")
        print(json.dumps(results, indent=2))
        
    except Exception as e:
        print(f"Error testing transition module: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_transition_module()