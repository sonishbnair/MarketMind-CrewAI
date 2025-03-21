# Market Update AI Crew

This is a multi-agent AI project where:
- A market research agent analyzes data for a user-provided stock ticker
- An analyst agent receives this research and generates a comprehensive summary report
- The report includes recommendations for option trading strategies

This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI.

## Setup Instructions

### Prerequisites

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```

### 1. Create a Miniconda Environment

```
brew install --cask miniconda
```


Commands

```
# Initialize conda (restart terminal after this)
conda init zsh 

# Create new environment
conda create -n ai-img-gen-env python=3.10
conda activate ai-img-gen-env

# Conda list enviorment
conda env list
```

### 2. Install CrewAI and CrewAI Tools

Follow the [official installation guide](https://docs.crewai.com/installation):

```bash
pip install crewai
pip install crewai-tools
```

Verify the installation:

```bash
pip freeze | grep crewai
```

Expected output:
```
crewai==0.100.0
crewai-tools==0.33.0
```

### 3. Create a Conda Environment

```bash
conda create -n "conda-crewai-env" python==3.12
conda env list conda-crewai-env
conda activate conda-crewai-env
```

### 4. Create Your First Crew Project

Follow the [quickstart guide](https://docs.crewai.com/quickstart) to get started:

```bash
crewai create crew market_update
```

## Project Structure

```
.
├── README.md
├── knowledge
│   └── user_preference.txt
├── output
│   └── reports stored here
├── pyproject.toml
├── src
│   └── market_update
│       ├── __init__.py
│       ├── config
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       ├── crew.py
│       ├── main.py
│       ├── other_tools
│       │   └── slack_messenger.py
│       └── tools
│           ├── __init__.py
│           ├── custom_tool.py
│           └── search_tool.py
└── tests
```

## Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/market_update/config/agents.yaml` to define your agents
- Modify `src/market_update/config/tasks.yaml` to define your tasks
- Modify `src/market_update/crew.py` to add your own logic, tools and specific args
- Modify `src/market_update/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the market_update Crew, assembling the agents and assigning them tasks as defined in your configuration.

Alternatively, you can run the main script directly:

```bash
python -m src.market_update.main <ticker_symbol>
```

## Features

- Market research agent that gathers comprehensive stock data
- Analysis agent that interprets data and provides trading recommendations
- Option strategy recommendations based on market conditions
- Configurable agent behaviors and expertise levels
- Extendable tool system for custom research capabilities
