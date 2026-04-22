# Troubleshooting Guide

## Common Issues and Solutions

### 1. ModuleNotFoundError: No module named 'apify'

**Problem:** The `apify` package is not installed.

**Solution:**
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install apify crawlee beautifulsoup4 langchain langchain-openai langchain-core openai lxml
```

**Note:** The correct package name is `apify` (not `apify-sdk` or `apify-client`). The `apify` package automatically installs `apify-client` as a dependency.

### 2. ModuleNotFoundError: No module named 'crawlee'

**Problem:** Crawlee is not installed.

**Solution:**
```bash
pip install crawlee
```

Crawlee is used for the BeautifulSoupCrawler which handles URL fetching with automatic retries.

### 3. ImportError: cannot import 'BeautifulSoupCrawler' from 'crawlee'

**Problem:** Wrong import path or outdated crawlee version.

**Solution:** Ensure you have crawlee >= 1.0.0. The correct import is:
```python
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext
```

### 4. No input data found / Missing old_url or new_url

**Problem:** The Actor can't find input data when running locally.

**Solution:** 
1. Create the input file at: `storage/key_value_stores/default/INPUT.json`
2. Format it like this:
```json
{
  "old_url": "https://example.com/terms/old",
  "new_url": "https://example.com/terms/new",
  "openai_api_key": "sk-your-key-here"
}
```

### 5. Crawl failures / Unable to fetch content from URLs

**Problem:** BeautifulSoupCrawler fails to fetch content.

**Solutions:**
- Check that URLs are accessible and valid
- Verify network connectivity
- Some sites may block automated requests - check if the site requires authentication or has rate limiting
- For archived URLs (like Wayback Machine), ensure the archive snapshot exists
- The crawler retries up to 3 times automatically; if all retries fail, check the Actor logs for the specific error

### 6. OpenAI API errors

**Problem:** Errors related to OpenAI API calls.

**Solutions:**
- Verify your OpenAI API key is correct in `INPUT.json`
- Check that you have credits/usage available on your OpenAI account
- Ensure the API key has the correct permissions

### 7. LLM returns invalid JSON

**Problem:** The analysis step fails to parse the LLM response.

**Solutions:**
- This is handled gracefully - the Actor falls back to `status: "CHANGED"`, `risk_level: "UNKNOWN"` with an error message
- If it happens consistently, check that the OpenAI API key has access to GPT-4o-mini
- The LLM is prompted to return strict JSON; markdown code fences are stripped automatically

### 8. Import errors with langchain

**Problem:** `langchain` or other langchain modules not found.

**Solution:**
```bash
pip install langchain langchain-openai langchain-core
```

### 9. Local testing without Apify platform

**Problem:** Want to test locally without Apify storage.

**Note:** The Actor requires Apify SDK for storage. For local testing:
1. Install all dependencies via `pip install -r requirements.txt`
2. Create the storage directory structure: `storage/key_value_stores/default/`
3. Place `INPUT.json` in that directory

### 10. Virtual Environment Issues

**Problem:** Dependencies conflict with system Python.

**Solution:** Use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Installation Steps

1. **Create virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up input file:**
   ```bash
   mkdir -p storage/key_value_stores/default
   # Edit storage/key_value_stores/default/INPUT.json with your URLs and API key
   ```

4. **Run the Actor:**
   ```bash
   python3 src/main.py
   ```

## Debugging Tips

1. **Enable verbose logging:** The Actor uses `Actor.log` which should show detailed information
2. **Check storage:** Verify that `storage/key_value_stores/default/` exists and contains your input
3. **Test individual components:** You can test the analysis function separately:
   ```python
   from src.analysis import analyze_changes
   result = await analyze_changes(old_text, new_text, api_key)
   # result is a dict with keys: status, risk_level, analysis
   ```

## Getting Help

If you encounter issues:
1. Check the error message carefully - it usually points to the problem
2. Verify all dependencies are installed: `pip list`
3. Check that INPUT.json is properly formatted JSON
4. Review the logs for specific error messages
