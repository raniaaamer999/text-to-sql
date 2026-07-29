import os
import asyncio
import json
from dotenv import load_dotenv
from toolbox_langchain import ToolboxClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

load_dotenv()

toolbox_url = "http://192.168.0.196:5001"

system_prompt = """
You're helping answer questions about a music store database.
Always check the table list before writing any SQL.
Don't guess a column name unless you've actually seen it come back from a tool.
Once you run the query use the result to answer the question in plain English.
"""

def extract_text(content):
    # gemini 3.6 sometimes returns content as a list of pieces instead of plain text
    # this just grabs the actual readable text and ignores the internal stuff
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") for block in content if isinstance(block, dict)
        )
    return str(content)


async def choose_chart_type(model, question, rows):
    # if there's no real tabular data, there's nothing to chart at all
    if not rows:
        return "none"

    sample = rows[:5]
    columns = list(rows[0].keys())

    chart_prompt = f"""
You are picking the best chart type for a question and the data it returned.

Question: {question}
Number of rows returned: {len(rows)}
Columns: {columns}
Sample rows: {sample}

Rules to follow:
- Use "pie" only if there are 8 or fewer rows and the numbers represent parts of one whole.
- Use "line" only if one of the columns is clearly a date, year, or something ordered over time.
- Use "bar" for comparing categories, especially when there are many rows, pie charts fall apart past a handful of slices.
- Use "none" if this isn't really chartable, like a single row with just one number in it.

Reply with exactly one word, nothing else: bar, line, pie, or none.
"""
    response = await model.ainvoke(chart_prompt)
    choice = extract_text(response.content).strip().lower()

    if choice not in ("bar", "line", "pie", "none"):
        choice = "bar"

    return choice


async def ask_agent(question):
    async with ToolboxClient(toolbox_url) as toolbox:
        tools = toolbox.load_toolset()

        model = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite",
        )

        agent = create_react_agent(model, tools, prompt=system_prompt)

        response = await agent.ainvoke({"messages": [("user", question)]})

        # go through every message and pull out any sql the agent actually ran
        sql_queries = []
        rows = None

        for message in response["messages"]:
            tool_calls = getattr(message, "tool_calls", None)
            if tool_calls:
                for call in tool_calls:
                    args = call.get("args", {})
                    # different tools name this differently, so check both common names
                    sql = args.get("sql") or args.get("query")
                    if sql:
                        sql_queries.append(sql)

            # separately, grab the actual real data that came back from running a query
            if getattr(message, "type", None) == "tool" and getattr(message, "name", None) == "execute_sql":
                try:
                    parsed = json.loads(message.content)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        rows = parsed
                except (json.JSONDecodeError, TypeError):
                    pass

        final_answer = extract_text(response["messages"][-1].content)

        chart_type = await choose_chart_type(model, question, rows)

        return {
            "answer": final_answer,
            "sql_queries": sql_queries,
            "rows": rows,
            "chart_type": chart_type,
        }


if __name__ == "__main__":
    test_question = "Who are the top 5 selling artists?"
    result = asyncio.run(ask_agent(test_question))
    print("answer:", result["answer"])
    print("sql used:", result["sql_queries"])
    print("chart type:", result["chart_type"])
