import asyncio
import gradio as gr
from agent import ask_agent

def handle_question(question):
    # gradio calls this normally, but our agent is async, so we wrap it here
    answer = asyncio.run(ask_agent(question))
    return answer

demo = gr.Interface(
    fn=handle_question,
    inputs=gr.Textbox(label="ask something about the music store"),
    outputs=gr.Textbox(label="answer"),
    title="text to sql agent",
)

if __name__ == "__main__":
    demo.launch()