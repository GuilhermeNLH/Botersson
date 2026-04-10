# 🤖 Botersson – Research Assistant Bot

> Discord bot for automated academic research: web search, patent analysis, article scraping, local AI classification (Ollama), Excel database management, MCP integration, and a full web GUI dashboard.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Web Search** | DuckDuckGo search (no API key) |
| ⚗️ **Patent Search** | Google Patents via scraping |
| 📚 **Article Search** | Semantic Scholar + arXiv (free APIs) |
| 🕷️ **Web Scraping** | Extract text from any URL |
| 🤖 **Local AI (Ollama)** | Classify content into macro/meso/micro themes |
| 📊 **Excel Database** | Auto-save all research to `.xlsx` with charts |
| 🌐 **Web GUI** | Dashboard to manage data, search, and configure |
| 🔗 **MCP Server** | Use with Claude Desktop / Cursor |
| 🎯 **Scoped Search** | Search by scope: web, news, academic, patents, github, government |
| 🇧🇷 **Portuguese AI Persona** | AI replies in Portuguese with a reflective Camus-inspired style |
| ⏰ **Automation** | Daily summary scheduler |
| 🍎 **macOS Compatible** | Works on macOS Ventura (Apple Silicon + Intel/Hackintosh) |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Ollama** (for local AI): [ollama.com](https://ollama.com)
- **Discord Bot Token**: [discord.com/developers](https://discord.com/developers/applications)

### macOS / Hackintosh (Ventura)

```bash
# 1. Install Homebrew (if needed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Python and Ollama
brew install python@3.11
brew install ollama

# 3. Pull an AI model (choose one)
ollama pull llama3.2        # Recommended – fast and accurate
# ollama pull mistral       # Alternative
# ollama pull phi3          # Lightweight option

# 4. Clone and set up Botersson
git clone https://github.com/GuilhermeNLH/Botersson.git
cd Botersson
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure
cp .env.example .env
# Edit .env: set DISCORD_TOKEN=your_token_here

# 6. Start everything
ollama serve &              # Start local LLM
python run.py               # Start bot + web GUI
```

### Windows / Linux

```bash
python -m venv venv
source venv/bin/activate    # Linux/macOS
# venv\Scripts\activate    # Windows

pip install -r requirements.txt
cp .env.example .env
# Edit .env

ollama serve &
python run.py
```

---

## 🎮 Discord Commands

All commands support both slash `/` and prefix `!` syntax.

### 🔍 Search
| Command | Description |
|---|---|
| `/search [scope] <query>` | Scoped search (`web`, `news`, `academic`, `patents`, `github`, `government`) |
| `/news <query>` | Search recent news |
| `/scrape <url>` | Extract text from a URL |

### ⚗️ Patents & Articles
| Command | Description |
|---|---|
| `/patent <query>` | Search Google Patents |
| `/article <query>` | Search Semantic Scholar |
| `/arxiv <query>` | Search arXiv preprints |
| `/analyze_patent <url> [topic]` | Scrape + AI classify a patent |
| `/analyze_article <url> [topic]` | Scrape + AI classify an article |

### 🤖 AI
| Command | Description |
|---|---|
| `/ask <question>` | Ask the local LLM a question |
| `/summarize <text>` | Summarize text with AI |
| `/classify <topic> <text>` | Classify text into macro/meso/micro themes |
| `/models` | List available Ollama models |

### 📊 Database / Excel
| Command | Description |
|---|---|
| `/db_summary` | Show record counts per sheet |
| `/chart [bar\|pie\|line] [topic]` | Generate a database chart |
| `/theme_chart [topic]` | Chart theme distribution |
| `/list_sheet [sheet] [limit]` | List entries from a sheet |
| `/add_theme <type> <name> [parent]` | Add a macro/meso/micro theme |
| `/export_excel` | Download the Excel file |

---

## 🌐 Web GUI

Access at **http://localhost:5000** after starting with `python run.py`.

| Page | URL | Features |
|---|---|---|
| **Dashboard** | `/` | Search, analyze URLs, charts, quick add themes |
| **Database** | `/excel` | Browse all sheets, add themes, export |
| **Settings** | `/settings` | Ollama config, MCP setup, Discord commands |

---

## 🔗 MCP Integration (Claude Desktop / Cursor)

Add to your MCP configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "botersson": {
      "command": "python",
      "args": ["-m", "bot.services.mcp_server"],
      "cwd": "/path/to/Botersson",
      "env": {
        "PYTHONPATH": "/path/to/Botersson"
      }
    }
  }
}
```

Available MCP tools: `search_web`, `search_in_scope`, `search_news`, `search_patents`, `search_articles`, `search_arxiv`, `scrape_url`, `scrape_patent`, `classify_content`, `summarize_text`, `answer_with_context`, `compare_sources`, `save_article`, `save_patent`, `get_database_summary`, `get_sheet_data`, `list_ollama_models`.

---

## 📁 Project Structure

```
Botersson/
├── bot/
│   ├── main.py              # Discord bot entry point
│   ├── cogs/
│   │   ├── search.py        # /search, /news, /scrape
│   │   ├── patents.py       # /patent, /article, /arxiv, /analyze_*
│   │   ├── ai.py            # /ask, /summarize, /classify, /models
│   │   └── excel.py         # /db_summary, /chart, /export_excel
│   ├── services/
│   │   ├── scraper.py       # Web scraping
│   │   ├── search_engine.py # DuckDuckGo search
│   │   ├── patent_search.py # Google Patents + Semantic Scholar + arXiv
│   │   ├── llm.py           # Ollama LLM integration
│   │   ├── excel_manager.py # Excel read/write/charts
│   │   └── mcp_server.py    # MCP server
│   └── utils/
│       └── helpers.py       # Shared utilities
├── web/
│   ├── app.py               # Flask web application
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # CSS + JS
├── data/                    # Excel files (auto-created)
├── config/
│   ├── config.yaml          # Application configuration
│   └── __init__.py          # Config loader
├── run.py                   # Unified launcher
├── requirements.txt
└── .env.example             # Environment template
```

---

## ⚙️ Configuration

Edit `config/config.yaml` or use environment variables in `.env`.

### Key `.env` variables

```env
DISCORD_TOKEN=your_token_here
OLLAMA_MODEL=llama3.2        # or mistral, phi3, llama3
OLLAMA_HOST=http://localhost:11434
WEB_PORT=5000
DATA_DIR=./data
```

### Launcher modes

```bash
python run.py           # Bot + Web GUI (default)
python run.py --bot     # Discord bot only
python run.py --web     # Web GUI only
python run.py --mcp     # MCP stdio server only
```

---

## 🛠️ Troubleshooting

**Ollama not responding:**
```bash
ollama serve                  # Start the server
ollama pull llama3.2          # Pull a model if none exists
```

**Discord slash commands not showing:**
- Ensure the bot has `applications.commands` scope
- It can take up to 1 hour for global commands to propagate
- Set `DISCORD_GUILD_ID` in `.env` for instant guild-specific sync

**Excel file location:**
```
data/research_data.xlsx
```
Change via `EXCEL_FILENAME` and `DATA_DIR` in `.env`.

---

## 📄 License

MIT – See [LICENSE](LICENSE) for details.
