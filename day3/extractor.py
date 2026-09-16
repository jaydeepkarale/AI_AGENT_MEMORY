import json

from ollama import chat


MODEL = "qwen3:4b"


def extract_memory(user_message: str) -> dict:

    prompt = f"""
You are the memory extraction component of an AI assistant.

Analyze the user's message and determine whether it contains
information that could be useful in future conversations.

Remember information such as:

- User identity
- Long-term goals
- Skills
- Occupation
- Preferences
- Long-term projects
- Important recurring activities
- Explicit requests to remember something

Do NOT remember:

- Greetings
- Casual conversation
- Questions
- Temporary information
- One-off actions
- Information useful only for the current response

A memory should represent information about the USER,
not information about the world in general.

Return ONLY valid JSON.

Schema:

{{
    "should_remember": true,
    "memory": "short factual statement",
    "memory_type": "semantic",
    "importance": 0.8,
    "confidence": 0.95,
    "reason": "short explanation"
}}

memory_type must be one of:

- semantic
- episodic
- procedural

importance must be between 0 and 1.

confidence must be between 0 and 1.

If nothing should be remembered:

{{
    "should_remember": false,
    "memory": "",
    "memory_type": "semantic",
    "importance": 0,
    "confidence": 0,
    "reason": "explanation"
}}

User message:

{user_message}
"""

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format="json",
    )

    content = response.message.content.strip()

    return json.loads(content)