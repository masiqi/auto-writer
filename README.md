# AI Essay Writing Assistant

An intelligent essay writing system powered by AutoGen and Deepseek LLM. This system uses multiple AI agents to collaborate on creating high-quality essays based on user requirements.

## Features

- Multiple specialized AI agents for different aspects of essay writing
- Real-time visualization of agent interactions
- Classical Chinese poetry integration
- Iterative improvement process
- User-friendly web interface
- Powered by Deepseek's language model

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory and add your Deepseek API key:
```
DEEPSEEK_API_KEY=your_api_key_here
```

3. Run the application:
```bash
streamlit run app.py
```

## System Architecture

The system consists of multiple specialized agents:
- RequirementAnalyst: Analyzes essay requirements
- WritingPlanner: Creates essay outline and strategy
- MaterialProvider: Gathers relevant materials
- PoemProvider: Finds matching classical poetry
- Writer: Composes the essay
- Polisher: Refines the language
- Reviewer: Evaluates and provides feedback
- Coordinator: Manages the overall process

## Usage

1. Enter your essay requirements in the web interface
2. Watch as the agents collaborate to create your essay
3. Review the final result and generated essay
