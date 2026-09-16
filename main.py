from agent import Agent
from memory import init_db, get_memories


USER_ID = "jaydeep"


def print_memories():

    memories = get_memories(USER_ID)

    print("\n" + "=" * 60)
    print("STORED MEMORIES")
    print("=" * 60)

    if not memories:
        print("No memories stored.")
        return

    for memory in memories:

        print(f"""
ID:          {memory[0]}
Memory:      {memory[1]}
Type:        {memory[2]}
Importance:  {memory[3]:.2f}
Confidence:  {memory[4]:.2f}
Created:     {memory[7]}
""")


def main():

    init_db()

    agent = Agent(USER_ID)

    print("=" * 60)
    print("AGENT MEMORY DEMO")
    print("=" * 60)

    print("""
Commands:

/memories  - show stored memories
/exit      - quit
""")

    while True:

        user_message = input("\nYou: ").strip()

        if not user_message:
            continue

        if user_message == "/exit":
            break

        if user_message == "/memories":
            print_memories()
            continue

        agent.chat(user_message)


if __name__ == "__main__":
    main()