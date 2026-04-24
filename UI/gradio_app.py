import os
import gradio as gr
from agent.core import SprintAgent

# Initialize agent
agent = SprintAgent()

# Absolute path for logo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")


# -----------------------
# Core Function
# -----------------------
def generate_plan(feature: str) -> str:
    if not feature.strip():
        return "Please enter a feature request."

    plan = agent.plan(feature)

    # Build structured output
    output = f"#{plan.get('feature_summary', '')}\n\n"

    for task in plan.get("tasks", []):
        output += f"## {task.get('id')} — {task.get('title')}\n"
        output += f"**Description:** {task.get('description')}\n\n"
        output += f"**Story Points:** {task.get('story_points')} | **Type:** {task.get('type')}\n\n"

        # Risks
        output += "**Risks:**\n"
        for r in task.get("risks", []):
            output += f"- {r}\n"

        # Acceptance Criteria
        output += "\n**Acceptance Criteria:**\n"
        for a in task.get("acceptance_criteria", []):
            output += f"- {a}\n"

        # Code Stub (collapsible)
        output += "\n<details><summary>Code Stub</summary>\n\n```python\n"
        output += task.get("code_stub", "")
        output += "\n```\n</details>\n\n---\n"

    # Sprint recommendation
    output += f"\n##Sprint Recommendation\n{plan.get('sprint_recommendation', '')}\n"

    # Unknowns
    output += "\n##Unknowns\n"
    for u in plan.get("unknowns", []):
        output += f"- {u}\n"

    return output


# -----------------------
# UI Layout
# -----------------------
with gr.Blocks() as demo:

    # Header (logo + title inline)
    with gr.Row():
        with gr.Column(scale=1, min_width=80):
            gr.Image(
                value=LOGO_PATH,
                width=60,
                show_label=False,
                container=False
            )

        with gr.Column(scale=6):
            gr.Markdown(
                """
                # SprintAgent  
                <span style="color:gray; font-size:14px;">
                AI-powered sprint planning & code generation
                </span>
                """
            )

    gr.Markdown("---")

    # Input box
    feature_input = gr.Textbox(
        lines=5,
        placeholder="Enter feature request...",
        label="Feature Request"
    )

    # Button
    generate_btn = gr.Button("Generate Plan")

    # Output (formatted markdown)
    output = gr.Markdown()

    # Button click action
    generate_btn.click(
        fn=generate_plan,
        inputs=feature_input,
        outputs=output
    )


# -----------------------
# Launch App
# -----------------------
demo.launch()