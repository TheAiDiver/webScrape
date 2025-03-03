import pandas as pd
from scraper import firecrawl_scraper
from utility import single_to_dataframe
from websiteParser import extract_websites
from extractor import (extract_info,
                       enhanced_json_extractor)

def main(text: str,
         prompt: str,
         output_path='scraped_data.csv'):
    """
    Main function that processes user input to extract websites, scrape data, and save results.
    
    This function performs four main operations:
    1. Extracts website URLs from the input text
    2. Scrapes content from these websites based on the input prompt
    3. Converts the scraped data into DataFrames and combines them
    4. Saves the scraped data to a CSV file
    
    Args:
        text (str): User input text containing website URLs and serving as the scraping prompt
        output_path (str, optional): Path to save the output CSV file
        
    Returns:
        pandas.DataFrame: A DataFrame containing the combined results from all websites
    """
    # Extract websites from the input text
    websites = extract_websites(text)  # --> input : list of websites
    print(f"Extracted websites: {websites}")
    
    # Initialize the main DataFrame
    main_df = None
    
    # Scrape data from the extracted websites
    for i, web in enumerate(websites):
        print(f"Processing website {i+1}/{len(websites)}: {web}")
        
        try:
            # Extract information from the website
            scraped_content = firecrawl_scraper(web)
            extracted_info = extract_info(scraped_content, prompt)
            single = enhanced_json_extractor(extracted_info)
            print(single)
            # Convert the result to a DataFrame
            single_df = single_to_dataframe(single)
            
            if single_df is not None and not single_df.empty:
                print(f"Extracted {len(single_df)} records with columns: {', '.join(single_df.columns)}")
                
                # Add source information
                single_df['source'] = web
                
                # Append to the main DataFrame
                if main_df is None:
                    main_df = single_df.copy()
                else:
                    # Ensure columns are aligned
                    for col in single_df.columns:
                        if col not in main_df.columns:
                            main_df[col] = None
                    
                    for col in main_df.columns:
                        if col not in single_df.columns:
                            single_df[col] = None
                    
                    # Concatenate
                    main_df = pd.concat([main_df, single_df], ignore_index=True)
                
                print(f"Current total records: {len(main_df)}")
            else:
                print(f"No data extracted from {web}")
        
        except Exception as e:
            print(f"Error processing website {web}: {str(e)}")
    
    # Save the scraped data to a CSV file if we have data
    if main_df is not None and not main_df.empty:
        main_df.to_csv(output_path, index=False)
        print(f"Data saved to {output_path}")
    else:
        print("No data to save")
    
    # Return the combined DataFrame
    return main_df if main_df is not None else pd.DataFrame()

if __name__ == "__main__":
    # Get user input for the query
    words = input("Please enter your search query: ")
    result_df = main(words)