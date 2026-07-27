import asyncio
import json
from agent import ask_agent

# your test questions, right here now instead of a separate file
questions = [
    "who are our top 5 selling artists",
    "how many customers do we have in brazil",
    "what's the total revenue broken down by country",
    "which employee has the most people reporting to them",
    "how many rock tracks do we have",
]


async def run_evaluation():
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