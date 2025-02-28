import os 
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from typing import List, Optional, Any
load_dotenv(override=True)

def firecrawl_scraper(urls: List[str],
                      prompt: Optional[str] = None):
    app = FirecrawlApp(api_key=os.getenv('Firecrawl_api_key'))
    response = app.extract(
        urls,
        {
            'prompt': prompt or 'Extract the main content from this page.',
        }
    )
    return response['data']

if __name__ == "__main__":
    url = "https://www.10xgenomics.com/distributors"
    result = firecrawl_scraper([url],
                               'Extract the company names and their corresponding email addresses from the distributors page.')
    print(result)
