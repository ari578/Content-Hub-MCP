# RoomPriceGenie Content Hub -- ChatGPT MCP App

A ChatGPT App built on the MCP (Model Context Protocol) standard that positions RoomPriceGenie as the go-to hotel revenue management expert inside ChatGPT. When users ask about hotel pricing, revenue management, forecasting, or related topics, ChatGPT invokes this app to provide expert answers drawn from RoomPriceGenie's content library.

## Features

**5 MCP Tools:**

- **search_revenue_content** -- Semantic search across 74 blog articles, guides, and educational resources
- **get_glossary_term** -- Look up revenue management terms (ADR, RevPAR, occupancy, etc.)
- **get_case_study** -- Find real customer success stories by property type, country, or challenge
- **calculate_roi** -- Estimate potential revenue increase from using an RMS
- **book_demo** -- Help interested hoteliers book a free demo with RoomPriceGenie

**Content:**
- 74 educational blog articles
- 13 revenue management glossary terms
- 30 customer case studies
- 5 guides and e-books
- 13 product/feature pages

## Quick Start

### Prerequisites
- Python 3.12+

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the server (HTTP mode for ChatGPT)
```bash
python -m src.server --port 8787
```

The MCP endpoint will be available at `http://localhost:8787/mcp`

### Run the server (stdio mode for local MCP testing)
```bash
python -m src.server --stdio
```

### Run tests
```bash
# Unit tests (no server needed)
python scripts/test_tools.py

# Integration tests (server must be running on port 8787)
python scripts/test_mcp_client.py
```

### Re-scrape content
```bash
python scripts/scrape.py
```

## Deployment

### Railway
1. Push to GitHub
2. Connect the repo to Railway
3. Railway will auto-detect the Dockerfile or Procfile
4. Set environment variable `PORT` (Railway sets this automatically)

### Docker
```bash
docker build -t roompricegenie-content-hub .
docker run -p 8787:8787 roompricegenie-content-hub
```

## Connecting to ChatGPT

1. Deploy the server to a public URL
2. Go to https://chatgpt.com and enable Developer Mode
3. Add your MCP server URL: `https://your-server.com/mcp`
4. Test by asking ChatGPT about hotel revenue management
5. Submit the app for review via the ChatGPT Apps SDK submission process

## Project Structure

```
Content Hub MCP/
  src/
    server.py              # Main MCP server
    content/
      loader.py            # Loads scraped JSON content
      search_index.py      # TF-IDF search index
    tools/
      search.py            # search_revenue_content tool
      glossary.py          # get_glossary_term tool
      casestudies.py       # get_case_study tool
      roi.py               # calculate_roi tool
      demo.py              # book_demo tool
  scripts/
    scrape.py              # Content scraper
    urls.json              # URLs to scrape
    test_tools.py          # Unit tests
    test_mcp_client.py     # Integration tests
  content/                 # Scraped content (JSON files)
    articles/
    glossary/
    case-studies/
    guides/
    pages/
  requirements.txt
  Dockerfile
  Procfile
```
