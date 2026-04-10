# Documentação de Funções do Botersson

Este documento lista as funções e métodos encontrados no código-fonte Python do projeto, com assinatura simplificada e objetivo resumido.

> Legenda: `?` indica parâmetro opcional/com valor padrão.

## `bot/cogs/ai.py`

- `def AICog.__init__(self, bot)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def AICog.ask(self, ctx, *, question)`
  - Ask the local LLM a question.
- `async def AICog.summarize(self, ctx, *, text)`
  - Summarize a block of text using the local LLM.
- `async def AICog.models(self, ctx)`
  - Show locally available Ollama models.
- `async def AICog.classify(self, ctx, topic, *, text)`
  - Use Ollama to classify text into macro/meso/micro research themes.
- `async def setup(bot)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.

## `bot/cogs/excel.py`

- `def ExcelCog.__init__(self, bot)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def ExcelCog.db_summary(self, ctx)`
  - Display row counts for each sheet in the Excel database.
- `async def ExcelCog.chart(self, ctx, chart_type=?, *, topic=?)`
  - Generate a chart showing database contents.
- `async def ExcelCog.theme_chart(self, ctx, *, topic=?)`
  - Generate a bar chart of themes distribution.
- `async def ExcelCog.list_sheet(self, ctx, sheet=?, limit=?)`
  - Show recent entries from a sheet.
- `async def ExcelCog.add_theme(self, ctx, theme_type, theme, parent=?, *, description=?)`
  - Add a theme to the database.
- `async def ExcelCog.export_excel(self, ctx)`
  - Send the Excel file as a Discord attachment.
- `async def setup(bot)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.

## `bot/cogs/patents.py`

- `def PatentsCog.__init__(self, bot)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def PatentsCog.patent(self, ctx, *, query)`
  - Search Google Patents.
- `async def PatentsCog.article(self, ctx, *, query)`
  - Search academic articles via Semantic Scholar.
- `async def PatentsCog.arxiv(self, ctx, *, query)`
  - Search arXiv preprints.
- `async def PatentsCog.analyze_patent(self, ctx, url, *, topic=?)`
  - Scrape a patent page and classify its content using Ollama.
- `async def PatentsCog.analyze_article(self, ctx, url, *, topic=?)`
  - Scrape an article page and classify its content using Ollama.
- `async def setup(bot)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.

## `bot/cogs/search.py`

- `def SearchCog.__init__(self, bot)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def SearchCog.search(self, ctx, *, query)`
  - Search the web using DuckDuckGo.
- `async def SearchCog.search_scope(self, ctx, scope, *, query)`
  - Search the web using a predefined scope.
- `async def SearchCog.news(self, ctx, *, query)`
  - Search recent news via DuckDuckGo.
- `async def SearchCog.scrape(self, ctx, url)`
  - Scrape a webpage and show its title and text excerpt.
- `async def setup(bot)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.

## `bot/main.py`

- `def Botersson.__init__(self)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def Botersson.setup_hook(self)`
  - Load all cogs and sync slash commands.
- `def Botersson._setup_scheduler(self)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def daily_summary()`
  - Send a daily summary to all guilds.
- `async def Botersson.on_ready(self)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def Botersson.on_command_error(self, ctx, error)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def main()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.

## `bot/services/excel_manager.py`

- `def ensure_workbook()`
  - Open existing workbook or create a new one with all required sheets.
- `def _write_header(ws, columns)`
  - Write a styled header row.
- `def _next_id(ws)`
  - Return next available row ID (max existing + 1).
- `def _append_row(ws, values)`
  - Append a row to the worksheet and return its row number.
- `def save_article(article, classification=?)`
  - Save an article to the Articles sheet. Returns the assigned ID.
- `def save_patent(patent, classification=?)`
  - Save a patent to the Patents sheet. Returns the assigned ID.
- `def save_search_result(result, query)`
  - Save a search result row. Returns the assigned ID.
- `def save_theme(theme_type, theme, parent=?, description=?)`
  - Save a macro/meso/micro theme. Returns the assigned ID.
- `def get_sheet_data(sheet_name)`
  - Read all rows from a sheet as list of dicts.
- `def get_all_sheets_summary()`
  - Return row count for each sheet.
- `def generate_chart(chart_type=?, topic=?)`
  - Generate a matplotlib chart of the current research data distribution.
- `def generate_themes_chart(topic=?)`
  - Generate a stacked bar chart showing themes distribution.
- `def workbook_path()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.

## `bot/services/llm.py`

- `def _call_ollama(prompt, system=?, model=?)`
  - Call the Ollama REST API and return the model's text response.
- `def list_ollama_models()`
  - Return list of locally available Ollama models.
- `def classify_content(text, title, topic)`
  - Use Ollama to classify content into macro/meso/micro themes.
- `def summarize_content(text, max_words=?)`
  - Summarize content using the LLM.
- `def compare_sources(sources, topic)`
  - Ask the LLM to compare multiple research sources.
- `def answer_question(question, context)`
  - Answer a user question based on scraped context.
- `async def async_classify(text, title, topic)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def async_summarize(text, max_words=?)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def async_compare(sources, topic)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def async_answer(question, context)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.

## `bot/services/mcp_server.py`

- `async def _execute_tool(name, arguments)`
  - Execute a named MCP tool and return the result.
- `async def run_mcp_server()`
  - Run the MCP stdio server (used by Claude Desktop / Cursor integration).
- `async def handle_list_tools()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def handle_call_tool(name, arguments)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def start_mcp_server_thread()`
  - Launch the MCP server in a background thread (for use alongside the bot).
- `def _run()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.

## `bot/services/patent_search.py`

- `def search_google_patents(query, max_results=?)`
  - Scrape Google Patents search results for a given query.
- `def scrape_patent_detail(patent_url)`
  - Scrape the full text of a Google Patent page.
- `def search_semantic_scholar(query, max_results=?)`
  - Search Semantic Scholar for academic articles (free API, no key needed).
- `def search_arxiv(query, max_results=?)`
  - Search arXiv preprints via their public API.
- `async def async_search_patents(query, max_results=?)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def async_scrape_patent(url)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def async_search_articles(query, max_results=?)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def async_search_arxiv(query, max_results=?)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.

## `bot/services/scraper.py`

- `def _next_ua()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def _clean_text(text)`
  - Remove excessive whitespace from scraped text.
- `def _validate_scrape_url(url)`
  - Return True only for safe http/https URLs that do not point to
- `def scrape_url(url)`
  - Synchronously scrape a URL and return a structured result.
- `async def async_scrape_url(url)`
  - Async wrapper around scrape_url.
- `async def scrape_multiple(urls)`
  - Scrape multiple URLs concurrently.

## `bot/services/search_engine.py`

- `def search_web(query, max_results=?)`
  - Search the web using DuckDuckGo.
- `def search_web_scoped(query, scope=?, max_results=?)`
  - Search with a predefined scope filter.
- `def search_news(query, max_results=?)`
  - Search recent news via DuckDuckGo news.
- `async def async_search_web(query, max_results=?)`
  - Async wrapper for search_web.
- `async def async_search_web_scoped(query, scope=?, max_results=?)`
  - Async wrapper for search_web_scoped.
- `async def async_search_news(query, max_results=?)`
  - Async wrapper for search_news.

## `bot/utils/helpers.py`

- `def truncate(text, max_len=?)`
  - Truncate a string to max_len characters, appending … if needed.
- `def paginate_embed(title, items, color=?, max_items=?)`
  - Create a simple embed with a list of items.
- `def success_embed(title, description=?)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def error_embed(title, description=?)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def info_embed(title, description=?)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.

## `config/__init__.py`

- `def _load_yaml()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def ExcelConfig.workbook_path(cls)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.

## `run.py`

- `def start_web_server()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `async def start_bot()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def parse_args()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def main()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.

## `web/app.py`

- `def _validate_url(url)`
  - Validate a user-supplied URL.
- `def index()`
  - Main dashboard.
- `def excel_page()`
  - Excel database management page.
- `def settings_page()`
  - Settings / configuration page.
- `def api_summary()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def api_sheet(sheet_name)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def api_chart()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def api_themes_chart()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def api_search()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def api_scrape()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def api_classify()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def api_analyze()`
  - Full pipeline: scrape URL → classify with AI → save to Excel.
- `def api_add_theme()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def api_export_excel()`
  - Download the Excel file.
- `def api_models()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def socket_search(data)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def socket_analyze(data)`
  - Sem docstring explícita; consulte o corpo da função para detalhes.
- `def run_web()`
  - Sem docstring explícita; consulte o corpo da função para detalhes.

