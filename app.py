"""
Gradio web interface for the CSUF food RAG system.

Run embed_retrieve.py once to build the vector store, then:
    python app.py
and open the printed local URL (default http://localhost:7860).
"""

import gradio as gr
from query import ask


def handle_query(question: str):
    if not question or not question.strip():
        return "Please enter a question.", ""

    result = ask(question)
    answer = result["answer"]
    sources = "\n".join(
        f"• {s['source']}" + (f"  ({s['url']})" if s["url"] else "")
        for s in result["sources"]
    ) or "(no sources retrieved)"
    return answer, sources


with gr.Blocks(title="CSUF Unofficial Food Guide") as demo:
    gr.Markdown(
        "# 🍔 CSUF Unofficial Food Guide\n"
        "Ask about food and dining options near Cal State Fullerton. "
        "Answers come **only** from scraped student reviews and local sources."
    )

    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. Where can I get cheap sushi near CSUF?",
        lines=2,
    )
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=5)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

    gr.Examples(
        examples=[
            "How much does the CSUF dining plan cost?",
            "What is a good spot for cheap sushi near Fullerton?",
            "What do reviewers say about the Gastronome?",
            "Where can I find vegan food near campus?",
        ],
        inputs=inp,
    )


if __name__ == "__main__":
    demo.launch()
