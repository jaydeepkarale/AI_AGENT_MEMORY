from extractor import extract_memory


test_messages = [
    "My name is Jaydeep.",
    "I prefer FastAPI over Django.",
    "What's the weather today?",
    "I'm preparing for a backend engineering interview."
]


for message in test_messages:

    print("\n" + "=" * 60)
    print("USER:", message)

    result = extract_memory(message)

    print("\nMEMORY DECISION:")
    print("Remember:", result["should_remember"])
    print("Memory:", result["memory"])
    print("Type:", result["memory_type"])
    print("Reason:", result["reason"])