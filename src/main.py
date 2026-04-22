"""
Main entry point for the ToS Watchdog Actor.
Uses Crawlee's BeautifulSoupCrawler to fetch and compare two ToS URLs.
"""
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from apify import Actor
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext

from src.analysis import analyze_changes


async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}
        old_url = input_data.get('old_url')
        new_url = input_data.get('new_url')
        openai_api_key = input_data.get('openai_api_key')

        if not old_url:
            Actor.log.error('old_url is required. Exiting.')
            return
        if not new_url:
            Actor.log.error('new_url is required. Exiting.')
            return
        if not openai_api_key:
            Actor.log.error('OpenAI API key is required.')
            return

        # Store scraped texts keyed by URL
        scraped_texts: dict[str, str] = {}

        crawler = BeautifulSoupCrawler(
            max_request_retries=3,
        )

        @crawler.router.default_handler
        async def handle_request(context: BeautifulSoupCrawlingContext) -> None:
            soup = context.soup
            # Remove non-content elements
            for tag in soup(["script", "style", "nav", "header", "footer"]):
                tag.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            cleaned = ' '.join(chunk for chunk in chunks if chunk)

            scraped_texts[context.request.url] = cleaned
            Actor.log.info(f'Scraped {len(cleaned)} chars from {context.request.url}')

        Actor.log.info(f'Crawling old URL: {old_url}')
        Actor.log.info(f'Crawling new URL: {new_url}')
        await crawler.run([old_url, new_url])

        old_text = scraped_texts.get(old_url, '')
        new_text = scraped_texts.get(new_url, '')

        if not old_text:
            Actor.log.error(f'Failed to scrape old URL: {old_url}')
        if not new_text:
            Actor.log.error(f'Failed to scrape new URL: {new_url}')

        if not old_text or not new_text:
            result = {
                'old_url': old_url,
                'new_url': new_url,
                'status': 'ERROR',
                'risk_level': 'UNKNOWN',
                'analysis': 'Failed to fetch one or both URLs.',
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }
            await Actor.push_data(result)
            print('\n' + '=' * 80)
            print('ACTOR OUTPUT (ERROR):')
            print('=' * 80)
            print(json.dumps(result, indent=2))
            print('=' * 80 + '\n')
            return

        if old_text == new_text:
            Actor.log.info('No changes detected - texts are identical')
            result = {
                'old_url': old_url,
                'new_url': new_url,
                'status': 'UNCHANGED',
                'risk_level': 'NONE',
                'analysis': 'No changes detected between the two versions.',
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }
            await Actor.push_data(result)
            print('\n' + '=' * 80)
            print('ACTOR OUTPUT:')
            print('=' * 80)
            print(json.dumps(result, indent=2))
            print('=' * 80 + '\n')
            return

        # Changes detected - analyze with LLM
        Actor.log.info('Changes detected. Analyzing with LLM...')
        try:
            analysis_result = await analyze_changes(old_text, new_text, openai_api_key)
            result = {
                'old_url': old_url,
                'new_url': new_url,
                'status': analysis_result['status'],
                'risk_level': analysis_result['risk_level'],
                'analysis': analysis_result['analysis'],
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            Actor.log.error(f'Error during analysis: {e}')
            result = {
                'old_url': old_url,
                'new_url': new_url,
                'status': 'CHANGED',
                'risk_level': 'UNKNOWN',
                'analysis': f'Error during LLM analysis: {e}',
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }

        await Actor.push_data(result)
        print('\n' + '=' * 80)
        print('ACTOR OUTPUT:')
        print('=' * 80)
        print(json.dumps(result, indent=2))
        print('=' * 80 + '\n')
        Actor.log.info('Comparison completed successfully.')


if __name__ == '__main__':
    asyncio.run(main())
