# Terms of Service Watchdog

An Apify Actor that compares two Terms of Service URLs (old vs new) and uses AI to analyze legal risk of changes.

## Overview

This Actor performs a one-time comparison between two Terms of Service URLs (old version vs new version). It crawls both URLs using Crawlee's BeautifulSoupCrawler, compares their content, and if differences are found, uses GPT-4o-mini to produce a structured risk assessment.

## Features

- **Crawlee-Powered Fetching**: Uses BeautifulSoupCrawler with built-in retries and request management
- **One-Time Analysis**: No stateful storage - perfect for ad-hoc comparisons
- **Change Detection**: Identifies differences between versions
- **AI-Powered Analysis**: Uses GPT-4o-mini to identify high-risk changes
- **Structured Output**: Returns status, risk level (with category), and detailed analysis

## Tech Stack

- **Python 3.12+**
- **Crawlee (BeautifulSoupCrawler)**: Web crawling with automatic retries and request management
- **BeautifulSoup4**: HTML parsing and text extraction
- **LangChain**: LLM orchestration
- **OpenAI GPT-4o-mini**: Legal risk analysis
- **Apify SDK**: Actor framework and storage

## Input Schema

```json
{
  "old_url": "https://example.com/terms/old",
  "new_url": "https://example.com/terms/new",
  "openai_api_key": "sk-..."
}
```

**Required Fields:**
- `old_url`: URL of the old/previous version to compare
- `new_url`: URL of the new/current version to compare
- `openai_api_key`: OpenAI API key for GPT-4o-mini analysis

## Output Schema

Results are saved to the default Dataset with the following structure:

```json
{
  "old_url": "https://example.com/terms/old",
  "new_url": "https://example.com/terms/new",
  "status": "CHANGED",
  "risk_level": "HIGH (Data Privacy)",
  "analysis": "The new terms explicitly introduce \"content analysis\" and \"machine learning\" as permitted uses for customer data...",
  "timestamp": "2024-01-01T12:00:00+00:00"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `CHANGED`, `UNCHANGED`, or `ERROR` |
| `risk_level` | string | Risk level with category, e.g. `HIGH (Data Privacy)`, `MEDIUM (Billing)`, `LOW (General)`, `NONE` |
| `analysis` | string | AI-generated plain-language analysis of legal implications |
| `old_url` | string | Old ToS URL |
| `new_url` | string | New ToS URL |
| `timestamp` | string | ISO 8601 UTC timestamp |

## Installation

### For Local Development/Testing

**Yes, you need to install dependencies before running locally:**

1. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up input file for local testing:
```bash
mkdir -p storage/key_value_stores/default
# Create storage/key_value_stores/default/INPUT.json with your configuration
```

Example `INPUT.json`:
```json
{
  "old_url": "https://example.com/terms/old",
  "new_url": "https://example.com/terms/new",
  "openai_api_key": "sk-your-openai-api-key-here"
}
```

**Note:** The `INPUT.json` file is already created in the project. Edit it with your actual URLs and API key.

### For Apify Platform

**No manual installation needed** - Dependencies are automatically installed during the Actor build process on Apify.

## Usage

### Local Development

After installing dependencies, you can run the Actor locally:

```bash
# Using Python directly
python src/main.py

# Or using Apify CLI (if installed)
apify run
```

**Note:** For local testing, you'll need:
- Python 3.12 or higher
- All dependencies from `requirements.txt` installed
- OpenAI API key (passed via input)
- Optional: Apify token if you want to use Apify storage locally

### Apify Platform

1. Push the Actor to Apify (dependencies install automatically)
2. Configure input with your old and new ToS URLs and OpenAI API key
3. Run the Actor to perform the comparison

## How It Works

1. **Crawl Both URLs**: BeautifulSoupCrawler fetches both URLs concurrently with automatic retry handling
2. **Text Extraction**: HTML is parsed; script, style, nav, header, and footer elements are stripped to produce clean text
3. **Text Comparison**: The two cleaned texts are compared directly
4. **LLM Analysis**: If texts differ, both versions are sent to GPT-4o-mini for structured analysis
5. **Risk Assessment**: The LLM returns a JSON response with:
   - **Status**: `CHANGED` or `UNCHANGED`
   - **Risk Level**: severity + category (e.g. `HIGH (Data Privacy)`)
   - **Analysis**: plain-language explanation of what changed and why it matters
6. **Output**: Results are saved to the Apify Dataset

## File Structure

```
tos_watchdog/
├── .actor/
│   ├── actor.json          # Actor manifest (name, version, schemas)
│   ├── INPUT_SCHEMA.json   # Input schema
│   └── output_schema.json  # Output schema
├── src/
│   ├── __init__.py         # Package marker
│   ├── main.py             # Entry point - Crawlee crawler + Actor lifecycle
│   └── analysis.py         # LangChain/OpenAI LLM integration
├── Dockerfile              # Container build (apify/actor-python:3.12)
├── requirements.txt        # Python dependencies
├── INPUT_SAMPLE.json       # Example input payload
└── storage/                # Local dev storage (key-value store, datasets)
```

## Notes

- **Stateless**: No persistent storage - each run is independent
- **Crawlee Retries**: BeautifulSoupCrawler handles retries automatically (3 attempts by default)
- **Text Extraction**: Removes scripts, styles, and navigation elements for cleaner comparison
- **Token Limits**: Both texts are limited to 15,000 characters each to stay within GPT-4o-mini token limits
- **Structured LLM Output**: The LLM is prompted to return JSON with status, risk_level, and analysis fields
- **Error Handling**: The Actor handles errors gracefully and reports them in the output
