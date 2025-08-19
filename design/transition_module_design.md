# Transition Module Design

## Overview
The transition module is designed to identify missing transition words between consecutive sentences within the same paragraph. It uses LLMs to analyze sentence pairs and suggest appropriate transition words when needed.

## Features
- Identifies consecutive sentences within paragraphs that lack proper transition words
- Uses configurable LLM services (Ollama or OpenAI)
- Highlights the first word of sentences that need transition words
- Provides explanations and suggestions for appropriate transition words
- Supports various types of transitions (contrast, addition, cause/effect, etc.)

## Configuration
The module uses two configuration files:
- `settings.json` - Contains LLM service configuration
- `.env` - Contains API keys for services that require them

### settings.json
```json
{
  "llm_service": {
    "service": "ollama",
    "host": "localhost",
    "port": 11434,
    "model": "gemma3:4b"
  }
}
```

### .env
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Implementation Details

### Sentence Parsing
The module splits text into paragraphs using double newlines as separators. Within each paragraph, it splits text into sentences based on periods.

### LLM Integration
The module supports two LLM services:
1. Ollama - For local LLM inference
2. OpenAI - For cloud-based LLM inference

### Prompt Design
The prompt is stored in a separate file `modules/transition_prompt.txt` and asks the LLM to:
1. Determine if there is a proper transition word connecting two sentences
2. If not, suggest appropriate candidates based on the relationship between sentences
3. If a transition word is already present, respond with transition: 0

### Response Format
The LLM should respond with a JSON object in this exact format:
```json
{
  "transition": 0 or 1,
  "candidate": ["candidate1", "candidate2", ...] or []
}
```

Where:
- `transition`: 0 means no transition needed, 1 means transition is needed
- `candidate`: Array of potential transition word candidates (empty if transition=0)

### Previous Context
The module includes up to 100 words of previous context in the prompt to help the LLM better understand the relationship between sentences.

## Usage
The module follows the standard module interface and can be used through:
1. The command-line interface using main.py
2. The web interface using web_interface.py

## Dependencies
- requests - For making HTTP requests to LLM services
- python-dotenv - For loading environment variables