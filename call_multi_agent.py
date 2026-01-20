import os
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

# -------------------------
# Agents
# -------------------------

coffee_research_agent = Agent(
    role="Coffee Research Specialist",
    goal="Research coffee bean types and flavor profiles using the web",
    backstory=(
        "You are a coffee expert who studies bean origins, roast levels, "
        "and flavor characteristics from trusted online sources."
    ),
    tools=[web_search_tool],
    llm=llm,
    verbose=True,
)

barista_agent = Agent(
    role="Professional Barista",
    goal="Create latte recipes tailored to specific coffee bean types",
    backstory=(
        "You are a world-class barista who designs latte recipes based on "
        "bean flavor profiles, roast level, and milk pairing."
    ),
    llm=llm,
    verbose=True,
)

# -------------------------
# Tasks
# -------------------------

research_task = Task(
    description=(
        "Research the most common coffee bean types (Arabica, Robusta, Liberica, Excelsa). "
        "For each, gather flavor notes, caffeine level, and best brewing characteristics."
    ),
    expected_output=(
        "A structured summary of each coffee bean type with flavor profile, "
        "caffeine content, and ideal use."
    ),
    agent=coffee_research_agent,
)

recipe_task = Task(
    description=(
        "Using the researched coffee bean information, create a latte recipe for each bean type. "
        "Each recipe should include:\n"
        "- Grind recommendation\n"
        "- Espresso ratio\n"
        "- Milk type\n"
        "- Optional flavor additions\n"
        "- Taste profile"
    ),
    expected_output=(
        "Four latte recipes, one per bean type, clearly formatted and easy to follow."
    ),
    agent=barista_agent,
)

# -------------------------
# Crew
# -------------------------

coffee_crew = Crew(
    agents=[coffee_research_agent, barista_agent],
    tasks=[research_task, recipe_task],
    process=Process.sequential,
    verbose=True,
)

# -------------------------
# Run
# -------------------------

if __name__ == "__main__":
    result = coffee_crew.kickoff()
    print("\n================ FINAL OUTPUT ================\n")
    print(result)
