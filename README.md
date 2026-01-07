# Suno Prompt Generator

A Streamlit web application for generating optimized music prompts for [Suno AI](https://suno.ai). Customize jazz music characteristics through various parameters and generate formatted prompts ready to paste into Suno.

## Features

- **Parameter-based prompt building**: Select from tonality, mode family, guitar style, groove, tempo, mood, era, and intro style
- **Auto-generated song titles**: Titles automatically reflect your parameter selections
- **Song history**: Save, load, and delete your prompt configurations
- **Batch generation**: Generate multiple random variations with parameter group locking
- **CSV export**: Export your saved songs or batch generations for A/B testing
- **AI Prompt Refiner**: OpenAI-powered agent that analyzes and optimizes your prompts for better Suno results

## Live Demo

🚀 [Try it on Streamlit Cloud](https://suno-prompt-generator.streamlit.app)

## Local Development

### Prerequisites
- Python 3.11+
- OpenAI API key (optional, for AI refiner feature)

### Setup

```bash
# Clone the repository
git clone https://github.com/stefanopiovesan/suno-prompt-generator.git
cd suno-prompt-generator

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Environment Variables

For the AI Prompt Refiner feature, you can set your OpenAI API key:

```bash
export OPENAI_API_KEY=your-key-here
```

Or enter it directly in the app (stored in session only, not persisted).

## Project Structure

```
├── app.py              # Main Streamlit application
├── data.py             # Prompt variation dictionaries
├── prompt_engine.py    # Prompt building logic
├── storage.py          # JSON persistence for song history
├── refiner.py          # OpenAI agent for prompt refinement
├── agent_tools.py      # Agent tool definitions
├── suno_knowledge.py   # Suno best practices knowledge base
└── requirements.txt    # Python dependencies
```

## AI Refiner Agent

The AI Prompt Refiner uses OpenAI's function calling to:
1. **Analyze** your prompt structure and keywords
2. **Check** Suno best practices from the knowledge base
3. **Refine** with production terms, arrangement hints, and effective keywords
4. **Validate** and score the result (1-10)

The agent reasoning steps are displayed in the UI so you can see how it improves your prompt.

## License

MIT
