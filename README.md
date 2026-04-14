# 🤖 Botersson – Bot Assistente de Pesquisa

> Bot para Discord focado em pesquisa acadêmica automatizada: busca na web, análise de patentes, scraping de artigos, classificação com IA local (Ollama), gerenciamento de banco em Excel, integração MCP e dashboard web completo.

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 🔍 **Busca na Web** | Busca com DuckDuckGo (sem chave de API) |
| ⚗️ **Busca de Patentes** | Google Patents via scraping |
| 📚 **Busca de Artigos** | Semantic Scholar + arXiv (APIs gratuitas) |
| 🕷️ **Web Scraping** | Extração de texto de qualquer URL |
| 🤖 **IA Local (Ollama)** | Classificação em temas macro/meso/micro |
| 📊 **Banco em Excel** | Salvamento automático em `.xlsx` com gráficos |
| 🌐 **Interface Web** | Dashboard para gerenciar dados, buscas e configurações |
| 🔗 **Servidor MCP** | Uso com Claude Desktop / Cursor |
| 🎯 **Busca por Escopo** | Busca por escopo: web, news, academic, patents, github, government |
| 🇧🇷 **Persona em Português** | Respostas da IA em português, com estilo reflexivo inspirado em Camus |
| ⏰ **Automação** | Agendador de resumo diário |
| 🍎 **Compatível com macOS** | Funciona no macOS Ventura (Apple Silicon + Intel/Hackintosh) |

---

## 🚀 Início Rápido

### Pré-requisitos

- **Python 3.10+**
- **Ollama** (para IA local): [ollama.com](https://ollama.com)
- **Token do Bot do Discord**: [discord.com/developers](https://discord.com/developers/applications)

### macOS / Hackintosh (Ventura)

```bash
# 1. Instale o Homebrew (se necessário)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Instale Python e Ollama
brew install python@3.11
brew install ollama

# 3. Baixe um modelo de IA (escolha um)
ollama pull llama3.2        # Recomendado – rápido e preciso
# ollama pull mistral       # Alternativa
# ollama pull phi3          # Opção mais leve

# 4. Clone e configure o Botersson
git clone https://github.com/GuilhermeNLH/Botersson.git
cd Botersson
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure
cp .env.example .env
# Edite o .env: defina DISCORD_TOKEN=your_token_here

# 6. Inicie tudo
ollama serve &              # Inicia o LLM local
python run.py               # Inicia bot + interface web
```

### Windows / Linux

```bash
python -m venv venv
source venv/bin/activate    # Linux/macOS
# venv\Scripts\activate    # Windows

pip install -r requirements.txt
cp .env.example .env
# Edite o .env

ollama serve &
python run.py
```

#### Windows (atalho .bat)

```bat
run_bot.bat
```

O script `run_bot.bat` automatiza o fluxo de terminal no Windows:
- cria `venv` (se necessário)
- instala dependências
- cria `.env` a partir de `.env.example` (na primeira execução)
- inicia `ollama serve`
- executa `python run.py`

---

## 🎮 Comandos do Discord

Todos os comandos funcionam tanto com slash `/` quanto com prefixo `!`.

### 🔍 Busca
| Comando | Descrição |
|---|---|
| `/search <query>` | Busca na web via DuckDuckGo |
| `/search_scope <scope> <query>` | Busca por escopo (`web`, `news`, `academic`, `patents`, `github`, `government`) |
| `/news <query>` | Busca de notícias recentes |
| `/scrape <url>` | Extrai texto de uma URL |

### ⚗️ Patentes e Artigos
| Comando | Descrição |
|---|---|
| `/patent <query>` | Busca no Google Patents |
| `/article <query>` | Busca no Semantic Scholar |
| `/arxiv <query>` | Busca de preprints no arXiv |
| `/analyze_patent <url> [topic]` | Scraping + classificação por IA de uma patente |
| `/analyze_article <url> [topic]` | Scraping + classificação por IA de um artigo |

### 🤖 IA
| Comando | Descrição |
|---|---|
| `/ask <question>` | Faz uma pergunta ao LLM local |
| `/summarize <text>` | Resume texto com IA |
| `/classify <topic> <text>` | Classifica texto em temas macro/meso/micro |
| `/models` | Lista modelos Ollama disponíveis |

### 📊 Banco de Dados / Excel
| Comando | Descrição |
|---|---|
| `/db_summary` | Mostra contagem de registros por planilha |
| `/chart [bar\|pie\|line] [topic]` | Gera gráfico do banco |
| `/theme_chart [topic]` | Gera gráfico de distribuição de temas |
| `/list_sheet [sheet] [limit]` | Lista entradas de uma planilha |
| `/add_theme <type> <name> [parent]` | Adiciona tema macro/meso/micro |
| `/export_excel` | Baixa o arquivo Excel |

---

## 🌐 Interface Web

Acesse em **http://localhost:5000** após iniciar com `python run.py`.

| Página | URL | Recursos |
|---|---|---|
| **Dashboard** | `/` | Busca, análise de URLs, gráficos, adição rápida de temas |
| **Banco de Dados** | `/excel` | Navegar por planilhas, adicionar temas, exportar |
| **Configurações** | `/settings` | Configuração do Ollama, setup MCP, comandos do Discord |

---

## 🔗 Integração MCP (Claude Desktop / Cursor)

Adicione no seu arquivo de configuração MCP:

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

Ferramentas MCP disponíveis: `search_web`, `search_in_scope`, `search_news`, `search_patents`, `search_articles`, `search_arxiv`, `scrape_url`, `scrape_patent`, `classify_content`, `summarize_text`, `answer_with_context`, `compare_sources`, `save_article`, `save_patent`, `get_database_summary`, `get_sheet_data`, `list_ollama_models`.

---

## 📁 Estrutura do Projeto

```
Botersson/
├── bot/
│   ├── main.py              # Ponto de entrada do bot do Discord
│   ├── cogs/
│   │   ├── search.py        # /search, /news, /scrape
│   │   ├── patents.py       # /patent, /article, /arxiv, /analyze_*
│   │   ├── ai.py            # /ask, /summarize, /classify, /models
│   │   └── excel.py         # /db_summary, /chart, /export_excel
│   ├── services/
│   │   ├── scraper.py       # Web scraping
│   │   ├── search_engine.py # Busca DuckDuckGo
│   │   ├── patent_search.py # Google Patents + Semantic Scholar + arXiv
│   │   ├── llm.py           # Integração com Ollama LLM
│   │   ├── excel_manager.py # Leitura/escrita/gráficos no Excel
│   │   └── mcp_server.py    # Servidor MCP
│   └── utils/
│       └── helpers.py       # Utilitários compartilhados
├── web/
│   ├── app.py               # Aplicação web Flask
│   ├── templates/           # Templates HTML Jinja2
│   └── static/              # CSS + JS
├── data/                    # Arquivos Excel (auto-criados)
├── config/
│   ├── config.yaml          # Configuração da aplicação
│   └── __init__.py          # Loader de configuração
├── run.py                   # Launcher unificado
├── requirements.txt
└── .env.example             # Template de variáveis de ambiente
```

---

## ⚙️ Configuração

Edite `config/config.yaml` ou use variáveis de ambiente no `.env`.

### Principais variáveis `.env`

```env
DISCORD_TOKEN=your_token_here
OLLAMA_MODEL=llama3.2        # ou mistral, phi3, llama3
OLLAMA_HOST=http://localhost:11434
WEB_PORT=5000
DATA_DIR=./data
```

### Modos de execução

```bash
python run.py           # Bot + Interface Web (padrão)
python run.py --bot     # Apenas bot do Discord
python run.py --web     # Apenas interface web
python run.py --mcp     # Apenas servidor MCP via stdio
```

---

## 🛠️ Solução de Problemas

**Ollama não responde:**
```bash
ollama serve                  # Inicie o servidor
ollama pull llama3.2          # Baixe um modelo se não houver nenhum
```

**Comandos slash do Discord não aparecem:**
- Garanta que o bot tenha o escopo `applications.commands`
- A propagação de comandos globais pode levar até 1 hora
- Defina `DISCORD_GUILD_ID` no `.env` para sincronização instantânea por guild

**Local do arquivo Excel:**
```
data/research_data.xlsx
```
Altere via `EXCEL_FILENAME` e `DATA_DIR` no `.env`.

---

## 📄 Licença

MIT – Veja [LICENSE](LICENSE) para detalhes.
