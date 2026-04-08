# Allergen Detector

A Chrome extension that detects allergens in product ingredient lists on Nykaa, Amazon India, and 1mg. When an allergen is found, an agentic AI pipeline automatically searches for and validates safe alternative products.

## Tech Stack

- **Browser Extension** — Chrome Manifest V3
- **Backend** — FastAPI (Python)
- **Scraping** — Playwright + BeautifulSoup
- **Agentic Framework** — LangGraph
- **LLM** — Groq API (Llama 3.3 70b)
- **Sites** — Nykaa, Amazon India, 1mg

## Architecture

The LangGraph agent runs in two phases:

**Phase 1 — Allergen Detection** (fast, ~30s)
- Scrapes product page ingredients
- Exact string match against user allergens

**Phase 2 — Alternative Search** (slow, ~2-3 mins)
- Searches same site for similar products
- Validates each alternative is allergen-free
- Returns top 3 safe alternatives

## Setup

1. Clone the repo
2. Create virtual environment
```bash
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
```
3. Create `.env` file
   GROQ_API_KEY=your_key_here

4. Run backend
```bash
   uvicorn main:app --reload
```
5. Load extension
   - Go to `chrome://extensions`
   - Enable Developer mode
   - Click Load unpacked → select `extension/` folder

## Project Structure

\```
allergen-detector/
├── main.py              # FastAPI endpoints
├── agent/
│   ├── graph.py         # LangGraph agent graphs
│   ├── nodes.py         # Agent nodes
│   ├── state.py         # State definition
│   └── llm.py           # Allergen detection logic
├── scrapers/
│   └── nykaa.py         # Nykaa scraper
└── extension/
    ├── manifest.json
    ├── background.js
    ├── content.js
    ├── popup.html
    └── popup.js
\```

