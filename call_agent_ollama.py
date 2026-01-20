import os
from datetime import datetime
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool

# Load environment variables
load_dotenv()

# -------------------------
# LLM (Ollama - Local)
# -------------------------
ollama_llm = LLM(model="ollama/llama3.1:latest", base_url="http://localhost:11434")

# -------------------------
# Define Agent
# -------------------------
research_agent = Agent(
    role="AI Research Analyst",
    goal="Research and summarize a given topic clearly and concisely",
    backstory=(
        "You are a senior AI researcher with deep experience in "
        "LLMs, agentic systems, and enterprise AI."
    ),
    llm=ollama_llm,
    verbose=True,
)

# -------------------------
# Define Task
# -------------------------
research_task = Task(
    description=(
        "Explain what agentic AI is and provide 3 real-world enterprise use cases."
    ),
    expected_output=(
        "A clear explanation of agentic AI followed by three bullet-pointed "
        "enterprise use cases."
    ),
    agent=research_agent,
)

# -------------------------
# Create Crew
# -------------------------
crew = Crew(
    agents=[research_agent],
    tasks=[research_task],
    process=Process.sequential,
    verbose=True,
)

# -------------------------
# Run
# -------------------------

if __name__ == "__main__":
    try:
        # Run the crew
        result = crew.kickoff()

        # Print to console
        print("\n================ FINAL OUTPUT ================\n")
        print(result)

        # Export to markdown file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crew_output_{timestamp}.md"

        with open(filename, "w") as f:
            f.write(f"# CrewAI Output - Agentic AI Research\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Model:** ollama/llama3.1:latest\n\n")
            f.write(f"**Agent:** AI Research Analyst\n\n")
            f.write(f"**Task:** Explain what agentic AI is and provide 3 real-world enterprise use cases.\n\n")
            f.write("---\n\n")
            f.write("## Result\n\n")
            f.write(str(result))

        print(f"\n✓ Output exported to: {filename}")

    except Exception as e:
        print(f"Error: {e}")