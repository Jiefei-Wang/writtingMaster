# Transition Module Prompt Design

## Objective
Design a prompt that will analyze two consecutive sentences and determine if they have proper transition words between them. If not, the LLM should suggest an appropriate transition word.

## Prompt Structure

### System Message
```
You are an expert writing assistant specializing in identifying and suggesting transition words between sentences. Your task is to analyze pairs of consecutive sentences and determine if they are properly connected with transition words.
```

### User Message Template
```
Analyze the following two consecutive sentences:

First sentence: "{first_sentence}"
Second sentence: "{second_sentence}"

Instructions:
1. Determine if there is a proper transition word or phrase connecting these sentences
2. If there is no transition word, suggest an appropriate one based on the relationship between the sentences
3. If there is already a transition word, respond with "TRANSITION_PRESENT" and nothing else

Response Format:
If no transition word is present:
***suggested_word*** where suggested_word is the first word of the second sentence highlighted with the suggested transition word inserted before it.

Provide your explanation and suggestion in the following JSON format:
{
  "span": "string",
  "suggestion": "string",
  "explanation": "string"
}

If a transition word is already present:
Respond with exactly: TRANSITION_PRESENT
```

## Example Interactions

### Example 1: Missing Transition
Input:
First sentence: "Research should promising result."
Second sentence: "we still do not understand its mechanism"

Output:
```
***However*** we still do not understand its mechanism
{
  "span": "***However*** we",
  "suggestion": "However",
  "explanation": "The sentences contrast each other - the first mentions promising results while the second indicates a lack of understanding. A contrasting transition word like 'However' would improve the flow."
}
```

### Example 2: Transition Present
Input:
First sentence: "The weather was beautiful."
Second sentence: "However, it started raining in the afternoon."

Output:
```
TRANSITION_PRESENT
```

## Implementation Notes

1. The LLM should be able to identify various types of transitions:
   - Addition: also, furthermore, moreover, additionally
   - Contrast: however, nevertheless, nonetheless, on the other hand
   - Cause/Effect: therefore, consequently, as a result, thus
   - Time/Sequence: first, next, then, finally, subsequently
   - Example: for example, for instance, specifically
   - Conclusion: in conclusion, to summarize, overall

2. The response format is critical for parsing the results in the module

3. When a transition word is already present, the LLM should respond with exactly "TRANSITION_PRESENT" to indicate no action is needed