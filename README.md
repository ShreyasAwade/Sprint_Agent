🚀 SprintAgent

AI-powered Sprint Planning & Code Generation System

SprintAgent converts natural language feature requests into structured
sprint plans, including: - Task breakdown - Dependencies - Code stubs -
Risks - Acceptance criteria - Execution strategy

------------------------------------------------------------------------

✨ Features

-   Natural Language → Structured Sprint Plan
-   Strict JSON Schema Output
-   Code Stub Generation (typed + structured)
-   Performance Evaluation (0–10,000 scale)
-   Benchmark vs Default LLM (Cursor Claude)
-   Retry & Schema Validation System
-   Interactive UI (Gradio)
-   Unit Tests for Evaluation Metrics

------------------------------------------------------------------------

🎯 Problem Statement

Developers often struggle to convert high-level feature ideas into
structured sprint plans.

Challenges include: - Breaking features into tasks - Defining
dependencies - Estimating effort - Generating implementation scaffolding

------------------------------------------------------------------------

❓ Why this problem?

-   Direct impact on developer productivity
-   Poor planning leads to delays and rework
-   Existing tools lack structured AI outputs

------------------------------------------------------------------------

🥇 Why this was prioritized?

-   High real-world relevance
-   Clear measurable outputs
-   Strong alignment with LLM capabilities
-   Combines AI + system design + engineering rigor

------------------------------------------------------------------------

🧠 Solution

SprintAgent transforms feature requests into: - Structured tasks
(Fibonacci story points) - Code-ready stubs with type hints - Execution
order and dependencies - Risk analysis - Testable acceptance criteria

------------------------------------------------------------------------

⚙️ Setup

1.  Clone Repo git clone cd sprint-agent

2.  Install Dependencies pip install -r requirements.txt

3.  Setup Environment (.env file) SPRINT_AGENT_API_KEY=your_api_key_here
    GROQ_MODEL=llama-3.3-70b-versatile

------------------------------------------------------------------------

▶️ Usage

Run CLI: python main.py

Run Benchmark: python main.py –benchmark

Run UI: python -m UI.gradio_app

Open browser: http://127.0.0.1:7860

------------------------------------------------------------------------

📊 Performance Evaluation

Score range: 0 to 10,000

Metrics: - Task Quality (3000) - Code Quality (2500) - Planning Accuracy
(2000) - Response Speed (1500) - JSON Reliability (1000)

Formula: Total Score = task_quality + code_quality + planning_accuracy +
response_speed + json_reliability

Example Score: 8600 / 10,000

------------------------------------------------------------------------

⚔️ Benchmark Comparison

SprintAgent vs Cursor Claude

-   Structured Output: Yes vs No
-   JSON Reliability: High vs Low
-   Task Breakdown: Detailed vs Generic
-   Code Stubs: Structured vs Basic
-   Planning Accuracy: Enforced vs Not enforced

------------------------------------------------------------------------

🧪 Testing

python -m pytest tests/

------------------------------------------------------------------------

🔐 Security

-   No API keys in code
-   Uses .env file
-   .env excluded via .gitignore

------------------------------------------------------------------------

📁 Project Structure

sprint-agent/ ├── agent/ ├── metrics/ ├── benchmarks/ ├── UI/ ├── tests/
├── main.py ├── requirements.txt ├── .env.example ├── .cursorrules └──
README.md

------------------------------------------------------------------------

🚀 Future Improvements

-   Pydantic validation
-   Multi-model support
-   SaaS deployment
-   Advanced UI enhancements

------------------------------------------------------------------------

👨‍💻 Author

Shreyas Awade
