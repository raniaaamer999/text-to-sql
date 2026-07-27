import os
import asyncio
from dotenv import load_dotenv
from toolbox_langchain import ToolboxClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

load_dotenv()

# TODO swap this for saadia's actual server url once she has it running
toolbox_url = "http://127.0.0.1:5000"

system_prompt = """
You're helping answer questions about a music store database.
Always check the table list before writing any SQL.
Don't guess a column name unless you've actually seen it come back from a tool.
Once you run the query use the result to answer the question in plain English.
"""

async def ask_agent(question):
    # opens a connection to the toolbox server and grabs whatever tools saadia set up
    async with ToolboxClient(toolbox_url) as toolbox:
        tools = toolbox.load_toolset()

        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
        )

        agent = create_react_agent(model, tools, prompt=system_prompt)

        response = await agent.ainvoke({"messages": [("user", question)]})
        return response["messages"][-1].content


if __name__ == "__main__":
    # quick manual test, swap this question to try different ones
    test_question = "Who are the top 5 selling artists?"
    answer = asyncio.run(ask_agent(test_question))
    print(answer)