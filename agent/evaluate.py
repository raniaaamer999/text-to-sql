import asyncio
import json
from agent import ask_agent


def load_test_questions():
    # opens the test file and turns the json text into an actual python list
    with open("test_queries.json") as f:
        return json.load(f)


async def run_evaluation():
    # grab your fixed list of five questions
    questions = load_test_questions()
    results = []

    # go through each question one at a time, keeping track of its number
    for i, question in enumerate(questions, start=1):
        print(f"\nquestion {i}: {question}")

        try:
            # actually ask the agent this question and wait for its answer
            answer = await ask_agent(question)
            print(f"answer: {answer}")
            results.append({"question": question, "answer": answer})

        except Exception as e:
            # if something breaks (like no server running yet) record that instead of crashing
            print(f"failed: {e}")
            results.append({"question": question, "answer": None, "error": str(e)})

    # write every question and answer out to a file so you have a record for later
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\ndone, saved to results.json")


if __name__ == "__main__":
    # only runs this whole thing if you run this file directly
    asyncio.run(run_evaluation())