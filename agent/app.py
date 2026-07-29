import asyncio
import gradio as gr
from agent import ask_agent

def handle_question(question):
    result = asyncio.run(ask_agent(question))
    sql_text = "\n\n".join(result["sql_queries"]) if result["sql_queries"] else "no sql was run"
    return result["answer"], sql_text

custom_css = """
.gradio-container {
    max-width: 720px !important;
    margin: auto !important;
}
#title {
    text-align: center;
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 4px;
}
#subtitle {
    text-align: center;
    color: #9298a8;
    margin-bottom: 24px;
}
"""

with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Text to SQL Agent", elem_id="title")
    gr.Markdown("Ask a question about the music store database.", elem_id="subtitle")

    question = gr.Textbox(
        label="Your question",
        placeholder="e.g. who are our top 5 selling artists",
        lines=2,
    )

    submit_btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer_output = gr.Textbox(label="Answer", lines=6)
        sql_output = gr.Code(label="SQL used", language="sql", lines=6)

    submit_btn.click(
        fn=handle_question,
        inputs=question,
        outputs=[answer_output, sql_output],
    )

if __name__ == "__main__":
    demo.launch()