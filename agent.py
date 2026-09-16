from ollama import chat

from extractor import extract_memory
from memory import save_memory
from retrieval import create_embedding, retrieve_memories


MODEL = "qwen3:4b"


class Agent:

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.messages = []

    def chat(self, user_message: str):

        # -----------------------------------------
        # 1. Retrieve relevant memories
        # -----------------------------------------

        memories = retrieve_memories(
            self.user_id,
            user_message,
            top_k=3,
        )

        memory_context = "\n".join(
            f"- {memory[2]}"
            for memory in memories
        )

        if not memory_context:
            memory_context = "No relevant memories."

        # -----------------------------------------
        # 2. Build prompt
        # -----------------------------------------

        prompt = f"""
You are a helpful AI assistant.

Relevant memories about the user:

{memory_context}

Use these memories when they are relevant.

Do not mention the memory system.

User's current message:

{user_message}
"""

        self.messages.append({
            "role": "user",
            "content": prompt,
        })

        # -----------------------------------------
        # 3. Generate response
        # -----------------------------------------

        stream = chat(
            model=MODEL,
            messages=self.messages,
            stream=True,
        )

        full_response = ""

        print("Agent: ", end="", flush=True)

        for chunk in stream:

            content = chunk.message.content

            print(
                content,
                end="",
                flush=True,
            )

            full_response += content

        print()

        self.messages.append({
            "role": "assistant",
            "content": full_response,
        })

        # -----------------------------------------
        # 4. Extract potential memory
        # -----------------------------------------

        print("\n[Extracting memory...]", flush=True)

        memory_candidate = extract_memory(user_message)

        print(
            f"[Memory decision: "
            f"{memory_candidate['should_remember']}]",
            flush=True,
        )


        # -----------------------------------------
        # 5. Store memory if appropriate
        # -----------------------------------------

        if memory_candidate["should_remember"]:

            content = memory_candidate["memory"]

            embedding = create_embedding(content)

            save_memory(
                user_id=self.user_id,
                content=content,
                memory_type=memory_candidate["memory_type"],
                importance=memory_candidate["importance"],
                confidence=memory_candidate["confidence"],
                embedding=embedding,
            )

            print(
                f"\n[Memory saved] {content}",
                flush=True,
            )

        return full_response