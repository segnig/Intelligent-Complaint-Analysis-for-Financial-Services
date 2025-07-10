import gradio as gr
import requests

from src.credit_rag_assistant import generate_answer


demo = gr.Interface(
    fn=generate_answer,
    inputs=gr.Textbox(lines=2, placeholder="Ask about complaints..."),
    outputs=[
        gr.Textbox(label="AI Answer", lines=6),
        gr.Textbox(label="Retrieved Sources", lines=10)
    ],
    title="CrediTrust Complaint Assistant",
    description="Ask about customer complaints for BNPL, Loans, Cards, and more.",
    allow_flagging="never"
)

demo.launch(debug=True)