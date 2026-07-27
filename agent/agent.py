import os
import asyncio
from dotenv import load_dotenv
from toolbox_langchain import ToolboxClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

load_dotenv()

toolbox_url = "http://192.168.1.42:5001"

system_prompt = """
You're helping answer questions about a music store database.
Always check the table list before writing any SQL.
Don't guess a column name unless you've actually seen it come back from a tool.
Once you run the query use the result to answer the question in plain English.
"""

async def ask_agent(question):
    async with ToolboxClient(toolbox_url) as toolbox:
        tools = toolbox.load_toolset()

        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
        )

        agent = create_react_agent(model, tools, prompt=system_prompt)

        response = await agent.ainvoke({"messages": [("user", question)]})

        # go through every message and pull out any sql the agent actually ran
        sql_queries = []
        for message in response["messages"]:
            tool_calls = getattr(message, "tool_calls", None)
            if tool_calls:
                for call in tool_calls:
                    args = call.get("args", {})
                    # different tools name this differently, so check both common names
                    sql = args.get("sql") or args.get("query")
                    if sql:
                        sql_queries.append(sql)

        final_answer = response["messages"][-1].content

        return {
            "answer": final_answer,
            "sql_queries": sql_queries,
        }


if __name__ == "__main__":
    test_question = "Who are the top 5 selling artists?"
    result = asyncio.run(ask_agent(test_question))
    print("answer:", result["answer"])
    print("sql used:", result["sql_queries"])