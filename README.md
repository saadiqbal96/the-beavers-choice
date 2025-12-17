#  Beaver's Choice Paper Company - Multi-Agent System

A comprehensive multi-agent AI system for intelligent inventory management, quote generation, and sales processing.

##  Project Overview

This project implements an intelligent multi-agent system using **smolagents** framework with **GPT-4o-mini** to handle customer inquiries, manage inventory, generate quotes, and process sales.

##  Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
pip install smolagents litellm

# Configure environment
cp .env.example .env
# Edit .env and add your UDACITY_OPENAI_API_KEY
```

### Running the System

```bash
cd src
python beaver_choice_multi_agent.py
```

##  Project Structure

```
 Beaver's Choice Multi-Agent System

 src/                               # Source Code
    beaver_choice_multi_agent.py   # Main implementation
    project_starter.py             # Helper functions

 docs/                              # Documentation
    PROJECT_REPORT.md
    agent_workflow_diagram.png
    agent_workflow_diagram.md

 data/                              # Data files
    quote_requests.csv
    quote_requests_sample.csv
    quotes.csv

 results/                           # Test results
    test_results.csv

 requirements.txt                   # Python dependencies
 .env.example                       # Environment template
 .gitignore                         # Git ignore rules
 README.md                          # This file
 PROJECT_STRUCTURE.md               # Detailed structure guide
```

##  Features

- **4 Specialized AI Agents** (Orchestrator, Inventory, Quoting, Sales)
- **9 Intelligent Tools** for all operations
- **Smart Pricing** with bulk discounts
- **Automated Inventory Management**
- **Real-time Financial Tracking**

##  Technology Stack

- **Framework**: smolagents v1.23.0
- **LLM Model**: GPT-4o-mini (via Vocareum)
- **Database**: SQLite with SQLAlchemy
- **Language**: Python 3.10+

##  Documentation

- [PROJECT_REPORT.md](docs/PROJECT_REPORT.md) - Complete system documentation
- [agent_workflow_diagram.md](docs/agent_workflow_diagram.md) - Workflow details

##  Author

**Saad Iqbal**
- GitHub: [@saadiqbal96](https://github.com/saadiqbal96)

---

**Made with  and **
