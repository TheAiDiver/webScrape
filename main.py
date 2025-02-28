from scraper import firecrawl_scraper
from websiteParser import extract_websites
from formatParser import save_to_csv

def main(text: str):
    """
    Main function that processes user input to extract websites, scrape data, and save results.
    
    This function performs three main operations:
    1. Extracts website URLs from the input text
    2. Scrapes content from these websites based on the input prompt
    3. Saves the scraped data to a CSV file
    
    Args:
        text (str): User input text containing website URLs and serving as the scraping prompt
        
    Returns:
        None: The function returns None after processing is complete
    """
    # Extract websites from the input text
    websites = extract_websites(text)
    print(websites)
    
    # Scrape data from the extracted websites using the input text as prompt
    distributors = firecrawl_scraper(websites, prompt=text)
    print(distributors)
    
    # Save the scraped data to a CSV file
    save_to_csv(distributors)
    return None

if __name__ == "__main__":
    # Get user input for the query
    words = input("Please enter your search query: ")
    result = main(words)
