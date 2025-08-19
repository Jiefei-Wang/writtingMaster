# Testing the Transition Module

## Prerequisites

1. Python 3.7 or higher
2. Required packages installed:
   ```
   pip install flask requests python-dotenv
   ```

## Testing with the Web Interface

1. Start the web interface:
   ```
   python run_web_interface.py
   ```

2. Access the interface at http://localhost:5000

3. Select the "transition" module from the available modules

4. Enter text with missing transitions, for example:
   ```
   Research should promising result.
   we still do not understand its mechanism.
   ```

5. Click "Run Selected Modules" to process the text

6. The module should highlight "we" and suggest "However" as a transition word

## Testing with the Command Line Interface

1. List available modules:
   ```
   python main.py --list-modules
   ```

2. Process text with the transition module:
   ```
   python main.py --text-file text/sample.txt --modules transition
   ```

## Expected Output

For text with missing transitions, the module should return results in the following format:
```json
{
  "transition": {
    "module_name": "transition",
    "module_description": "Identifies missing transition words between consecutive sentences within the same paragraph",
    "results": [
      {
        "text_span": "***However*** we",
        "position": 45,
        "explanation": "Lack of transition, needs word: However. Potential candidates: However, Nevertheless, Nonetheless, But"
      }
    ]
  }
}
```

## Configuration

The module uses two configuration files:
- `settings.json` - Contains LLM service configuration
- `.env` - Contains API keys for services that require them

Make sure these files are properly configured for your environment.

## Prompt Template

The module uses a separate prompt template file located at `modules/transition_prompt.txt`. This file can be modified to adjust how the LLM analyzes sentence pairs.

## LLM Response Format

The module expects the LLM to respond with a JSON object in this format:
```json
{
  "transition": 0 or 1,
  "candidate": ["candidate1", "candidate2", ...] or []
}
```

Where:
- `transition`: 0 means no transition needed, 1 means transition is needed
- `candidate`: Array of potential transition word candidates (empty if transition=0)