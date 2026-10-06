# The Agentic Advantage

A collection of examples demonstrating AI agent patterns and multi-agent orchestration using CrewAI and Ollama.

## Overview

This project showcases different agentic AI patterns and architectures, from simple single-agent systems to complex multi-agent workflows. All examples use locally-running Ollama with the Llama 3.1 model.

## Files

### 1. [call_agent_ollama.py](call_agent_ollama.py)
Basic single-agent setup demonstrating:
- Simple agent creation with CrewAI
- Task definition and execution
- Output export to markdown files
- Error handling

**Use Case:** Research and explain agentic AI concepts with enterprise use cases.

### 2. [call_multi_agent.py](call_multi_agent.py)
Multi-agent collaboration example featuring:
- **Coffee Research Specialist**: Web-enabled agent for researching coffee bean types
- **Professional Barista**: Recipe creation agent
- Sequential task execution with information passing between agents

**Use Case:** Research coffee beans and create specialized latte recipes for each type.

### 3. [call_agent_patterns.py](call_agent_patterns.py)
Comprehensive demonstration of four distinct agent patterns:

**Pattern 1: Single Agent (Baseline)**
- Simple autonomous agent handling complete task

**Pattern 2: Planner → Executor**
- Planning agent breaks down problems
- Executor agent implements the plan

**Pattern 3: Tool-Augmented Research Agent**
- Agent with web search capabilities via SerperDev

**Pattern 4: Critic / Reflection Agent**
- Evaluates outputs and suggests improvements

**Use Case:** Explores coffee bean types and latte recipes through different architectural approaches.

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai/) installed and running locally
- Llama 3.1 model pulled in Ollama: `ollama pull llama3.1:latest`
- SerperDev API key (for web search functionality)

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv_ai
   source venv_ai/bin/activate  # On Windows: venv_ai\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root:
   ```
   SERPER_API_KEY=your_serper_api_key_here
   ```

## Usage

### Run the basic single-agent example:
```bash
python call_agent_ollama.py
```
Output will be saved to a timestamped markdown file.

### Run the multi-agent example:
```bash
python call_multi_agent.py
```

### Run the agent patterns comparison:
```bash
python call_agent_patterns.py
```

## Dependencies

- `crewai` - Multi-agent orchestration framework
- `crewai-tools` - Tools for CrewAI agents (includes SerperDevTool)
- `langchain-ollama` - Ollama integration for LangChain
- `python-dotenv` - Environment variable management
- `litellm` - LLM proxy and unified API
- `openai~=1.83.0` - OpenAI API client

## Configuration

All examples are configured to use:
- **Model**: `ollama/llama3.1:latest`
- **Base URL**: `http://localhost:11434`
- **Process**: Sequential task execution
- **Verbose mode**: Enabled for detailed logging

## Agent Patterns Explained

### Single Agent
Best for straightforward tasks with clear requirements. The agent handles the entire workflow autonomously.

### Planner-Executor
Separates strategic planning from execution. Useful when tasks require structured decomposition.

### Tool-Augmented
Enhances agent capabilities with external tools like web search. Essential for tasks requiring real-time information.

### Critic/Reflection
Adds quality control through evaluation and iteration. Improves output quality through feedback loops.

## License

This project is for educational and demonstration purposes.

## Jev as a LangChain classifier

[`jev_langchain/`](jev_langchain/) shows TypeSafe's Jev (a System One classifier) used through LangChain for loan-email triage. It needs only `TYPESAFE_API_KEY` in your environment, not a chat-model key. See its README.
