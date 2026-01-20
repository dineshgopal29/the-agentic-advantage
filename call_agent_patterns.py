import os
import sys
from datetime import datetime
from io import StringIO
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool

# Load environment variables
load_dotenv()

# -------------------------
# LLM (Ollama - Local)
# -------------------------
llm = LLM(model="ollama/llama3.1:latest", base_url="http://localhost:11434")

# -------------------------
# Tools
# -------------------------
web_search_tool = SerperDevTool()

# ======================================================
# PATTERN 1: Single Agent (Baseline)
# ======================================================

single_agent = Agent(
    role="Coffee Enthusiast",
    goal="Learn about coffee beans and create latte recipes",
    backstory="You love coffee and enjoy experimenting with latte recipes.",
    llm=llm,
    verbose=True
)

single_task = Task(
    description=(
        "Explain common coffee bean types and create one latte recipe "
        "that works well for each type."
    ),
    expected_output="Explanation followed by multiple latte recipes.",
    agent=single_agent
)

# ======================================================
# PATTERN 2: Planner → Executor
# ======================================================

planner_agent = Agent(
    role="Planner Agent",
    goal="Break down the coffee learning problem into clear steps",
    backstory="You excel at decomposing problems into structured plans.",
    llm=llm,
    verbose=True
)

executor_agent = Agent(
    role="Executor Agent",
    goal="Execute the plan and generate high-quality latte recipes",
    backstory="You follow plans carefully and execute with precision.",
    llm=llm,
    verbose=True
)

planning_task = Task(
    description=(
        "Create a step-by-step plan to research coffee beans "
        "and produce latte recipes tailored to each type."
    ),
    expected_output="A numbered execution plan.",
    agent=planner_agent
)

execution_task = Task(
    description=(
        "Follow the plan and generate latte recipes for each coffee bean type."
    ),
    expected_output="Well-structured latte recipes.",
    agent=executor_agent
)

# ======================================================
# PATTERN 3: Tool-Augmented Research Agent
# ======================================================

research_agent = Agent(
    role="Coffee Research Agent",
    goal="Research coffee beans using the web",
    backstory="You research coffee origins, flavors, and roast profiles.",
    tools=[web_search_tool],
    llm=llm,
    verbose=True
)

research_task = Task(
    description=(
        "Research Arabica, Robusta, Liberica, and Excelsa coffee beans. "
        "Include flavor notes and ideal brewing characteristics."
    ),
    expected_output="A structured research summary for each bean type.",
    agent=research_agent
)

# ======================================================
# PATTERN 4: Critic / Reflection Agent
# ======================================================

critic_agent = Agent(
    role="Coffee Critic",
    goal="Evaluate latte recipes and suggest improvements",
    backstory="You are a professional coffee critic with refined taste.",
    llm=llm,
    verbose=True
)

critic_task = Task(
    description=(
        "Review the generated latte recipes and suggest improvements "
        "for balance, flavor pairing, and clarity."
    ),
    expected_output="Actionable feedback and refined recipe suggestions.",
    agent=critic_agent
)

# ======================================================
# Crew Orchestration
# ======================================================

crew = Crew(
    agents=[
        single_agent,
        planner_agent,
        executor_agent,
        research_agent,
        critic_agent
    ],
    tasks=[
        single_task,
        planning_task,
        execution_task,
        research_task,
        critic_task
    ],
    process=Process.sequential,
    verbose=True
)

# -------------------------
# Helper Function for Log Formatting
# -------------------------
def format_logs_to_markdown(logs):
    """Format raw logs into readable markdown sections"""
    lines = logs.split('\n')
    formatted = []
    current_section = None

    for line in lines:
        # Detect section headers
        if '=' * 40 in line:
            if current_section:
                formatted.append('\n')
            continue

        # Detect agent execution start
        if 'Working Agent:' in line:
            if current_section:
                formatted.append('\n')
            agent_name = line.split('Working Agent:')[-1].strip()
            formatted.append(f"## {agent_name}\n")
            current_section = 'agent'
            continue

        # Detect task start
        if 'Task:' in line and not line.strip().startswith('#'):
            formatted.append(f"\n**Task:** {line.split('Task:')[-1].strip()}\n")
            continue

        # Detect final output section
        if 'FINAL OUTPUT' in line:
            formatted.append('\n---\n\n## Final Output\n\n')
            current_section = 'final'
            continue

        # Detect thought process
        if line.strip().startswith('Thought:'):
            formatted.append(f"\n**Thought:**\n> {line.split('Thought:')[-1].strip()}\n")
            continue

        # Detect action
        if line.strip().startswith('Action:'):
            formatted.append(f"\n**Action:** `{line.split('Action:')[-1].strip()}`\n")
            continue

        # Detect observation
        if line.strip().startswith('Observation:'):
            formatted.append(f"\n**Observation:**\n```\n")
            formatted.append(line.split('Observation:')[-1].strip())
            formatted.append('\n```\n')
            continue

        # Detect execution start timestamp
        if 'Agent Patterns Execution Started at:' in line:
            formatted.append(f"**Execution Started:** {line.split('at:')[-1].strip()}\n\n")
            formatted.append('---\n\n')
            continue

        # Add regular lines
        if line.strip():
            # Clean up ANSI color codes if any
            clean_line = line.replace('\x1b[1m', '').replace('\x1b[0m', '')
            clean_line = clean_line.replace('\x1b[95m', '').replace('\x1b[92m', '')

            if current_section == 'final':
                formatted.append(f"{clean_line}\n")
            elif clean_line.strip():
                formatted.append(f"{clean_line}\n")

    return ''.join(formatted)


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    # Capture output
    log_capture = StringIO()
    original_stdout = sys.stdout

    class TeeOutput:
        def __init__(self, *outputs):
            self.outputs = outputs

        def write(self, text):
            for output in self.outputs:
                output.write(text)

        def flush(self):
            for output in self.outputs:
                output.flush()

    # Redirect stdout to both console and log capture
    sys.stdout = TeeOutput(original_stdout, log_capture)

    try:
        print(f"Agent Patterns Execution Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        result = crew.kickoff()

        print("\n" + "=" * 80)
        print("================ FINAL OUTPUT ================")
        print("=" * 80 + "\n")
        print(result)

    finally:
        # Restore original stdout
        sys.stdout = original_stdout

        # Get captured logs
        logs = log_capture.getvalue()
        log_capture.close()

        # Save to markdown file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agent_patterns_output_{timestamp}.md"

        # Format logs for better readability
        formatted_logs = format_logs_to_markdown(logs)

        with open(filename, "w") as f:
            f.write(f"# Agent Patterns Execution Log\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Model:** ollama/llama3.1:latest\n\n")
            f.write(f"**Patterns Demonstrated:**\n")
            f.write(f"- Pattern 1: Single Agent (Baseline)\n")
            f.write(f"- Pattern 2: Planner → Executor\n")
            f.write(f"- Pattern 3: Tool-Augmented Research Agent\n")
            f.write(f"- Pattern 4: Critic / Reflection Agent\n\n")
            f.write("---\n\n")
            f.write(formatted_logs)

        print(f"\n✓ Logs and output exported to: {filename}")