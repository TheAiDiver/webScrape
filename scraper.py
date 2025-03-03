import os 
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from typing import List, Optional, Any
load_dotenv(override=True)

def firecrawl_scraper(url: str):
    app = FirecrawlApp(api_key=os.getenv('Firecrawl_api_key'))
    response = app.scrape_url(
        url=url,
        params={
            'formats': ['markdown'],
        }
    )
    return response['markdown']

if __name__ == "__main__":
    url = "https://www.10xgenomics.com/distributors"
    result = firecrawl_scraper(url)
    print(result)
