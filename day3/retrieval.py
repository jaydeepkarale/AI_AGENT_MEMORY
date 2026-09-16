import json
import math

from ollama import embed

from memory import get_memories


EMBEDDING_MODEL = "nomic-embed-text"


def create_embedding(text: str) -> list[float]:
    response = embed(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.embeddings[0]


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def retrieve_memories(
    user_id: str,
    query: str,
    top_k: int = 3,
):
    query_embedding = create_embedding(query)

    memories = get_memories(user_id)

    scored_memories = []

    for memory in memories:

        memory_id = memory[0]
        content = memory[1]
        memory_type = memory[2]
        importance = memory[3]
        confidence = memory[4]
        embedding_json = memory[5]

        if not embedding_json:
            continue

        memory_embedding = json.loads(embedding_json)

        similarity = cosine_similarity(
            query_embedding,
            memory_embedding,
        )

        # Simple ranking formula for our demo.
        score = (
            similarity * 0.7
            + importance * 0.2
            + confidence * 0.1
        )

        scored_memories.append(
            (
                score,
                memory_id,
                content,
                memory_type,
            )
        )

    scored_memories.sort(
        reverse=True,
        key=lambda item: item[0],
    )

    return scored_memories[:top_k]