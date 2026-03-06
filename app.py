from agent_loop import run_agent


def main():
    print("Local Agent started. Type 'exit' to quit.\n")

    while True:
        user_input = input("You> ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Bye.")
            break

        try:
            answer = run_agent(user_input)
            print(f"Agent> {answer}\n")
        except Exception as e:
            print(f"Agent> error: {e}\n")


if __name__ == "__main__":
    main()