# Multi-Agent Storybook Generator

A sophisticated multi-agent system built with LangGraph that generates personalized visual storybooks for children. The system uses specialized AI agents to create cohesive, engaging stories with consistent illustrations.

## Features

- **Multi-Agent Architecture**: Specialized agents for different aspects of book creation
- **Visual Storytelling**: Balanced text and illustrations on each page
- **Consistency Management**: Ensures character and style consistency throughout
- **Age-Appropriate Content**: Tailored content for different age groups
- **Interactive Interface**: Streamlit-based web interface for easy book creation

## Agents

1. **Overall Book & Character Planner**: Defines story arc, setting, and characters
2. **Consistency Planner**: Ensures coherence across chapters, characters, and themes
3. **Chapter Writer**: Writes engaging, age-appropriate text
4. **Visual Designer**: Creates illustrations for each page
5. **Image Consistency Agent**: Maintains uniform character designs and style

## Installation

```bash
pip install -r requirements.txt
```

## Setup

1. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

2. Run the Streamlit interface:
```bash
streamlit run app.py
```

## Usage

1. Open the web interface
2. Enter book parameters (genre, age group, theme, etc.)
3. Generate your storybook
4. Download the completed book as PDF

## Project Structure

```
├── agents/           # Individual agent implementations
├── models/           # Data models and schemas
├── utils/            # Utility functions
├── app.py           # Streamlit web interface
├── main.py          # Main execution script
└── requirements.txt # Dependencies
```
