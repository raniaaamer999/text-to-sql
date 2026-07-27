import asyncio
import gradio as gr
from agent import ask_agent

def handle_question(question):
    result = asyncio.run(ask_agent(question))
    sql_text = "\n\n".join(result["sql_queries"]) if result["sql_queries"] else "no sql was run"
    return result["answer"], sql_text

demo = gr.Interface(
    fn=handle_question,
    inputs=gr.Textbox(label="ask something about the music store"),
    outputs=[
        gr.Textbox(label="answer"),
        gr.Textbox(label="sql used"),
    ],
    title="text to sql agent",
)

if __name__ == "__main__":
    demo.launch()