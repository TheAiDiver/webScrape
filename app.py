import os
import pandas as pd
import streamlit as st
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
        text (str): User input text containing website URLs
        prompt (str): Prompt for extracting information
        output_path (str, optional): Path to save the output CSV file
        
    Returns:
        pandas.DataFrame: A DataFrame containing the combined results from all websites
    """
    # Extract websites from the input text
    websites = extract_websites(text)
    
    # Initialize the main DataFrame
    main_df = None
    
    # Scrape data from the extracted websites
    for i, web in enumerate(websites):
        try:
            # Extract information from the website
            scraped_content = firecrawl_scraper(web)
            extracted_info = extract_info(scraped_content, prompt)
            single = enhanced_json_extractor(extracted_info)
            
            # Convert the result to a DataFrame
            single_df = single_to_dataframe(single)
            
            if single_df is not None and not single_df.empty:
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
            
        except Exception as e:
            print(f"Error processing website {web}: {str(e)}")
    
    # Save the scraped data to a CSV file if we have data
    if main_df is not None and not main_df.empty:
        main_df.to_csv(output_path, index=False)
    
    # Return the combined DataFrame
    return main_df if main_df is not None else pd.DataFrame()


def streamlit_app():
    """
    Streamlit application that provides a UI for the web scraping functionality.
    """
    # App title and description
    st.title("Psr Web Scraping Agent")
    st.markdown("""
    This app helps extract website URLs from text, scrape content from these websites,
    and save the results to a CSV file.
    
    **Instructions:**
    1. Enter text containing website URLs in the text area below
    2. Customize the extraction prompt if needed
    3. Click 'Process' to start the extraction and scraping process
    4. View the results and download the CSV file
    
    """)
    
    # User input text area
    user_input = st.text_area("Enter website URLs:", 
                             height=150,
                             help="Enter website URLs that you want to scrape",
                             placeholder="Example: https://www.creative-biolabs.com/search.aspx?key=Anapoe&ty=tag and https://www.creative-biolabs.com/search.aspx?key=NG%20class&ty=tag")
    
    # Custom prompt for extraction
    extraction_prompt = st.text_input("Extraction prompt:", 
                                    value="帮我抓取产品和对应的产品Molecular Formula",
                                    help="Customize the prompt used for extracting information from scraped content.")
    
    # Output filename
    output_filename = st.text_input("Output filename:", 
                                   value="scraped_data.csv",
                                   help="Specify the filename for the CSV output.")
    
    # Process button
    if st.button("Process"):
        if not user_input:
            st.error("Please enter some text first.")
        else:
            # Create a status message
            status = st.empty()
            
            try:
                # Step 1: Extract websites
                status.info("Extracting websites from text...")
                websites = extract_websites(user_input)
                
                if not websites:
                    st.warning("No websites were found in the text.")
                    return
                
                # Display extracted websites
                st.subheader("Extracted Websites")
                st.write(websites)
                
                # Step 2: Process the websites
                status.info("Processing websites. This may take a while...")
                
                # Create a progress bar
                progress_bar = st.progress(0)
                
                # Process websites one by one with visible progress
                main_df = None
                for i, web in enumerate(websites):
                    # Update status for current website
                    sub_status = st.empty()
                    sub_status.info(f"Processing website {i+1}/{len(websites)}: {web}")
                    
                    try:
                        # Extract information from the website
                        scraped_content = firecrawl_scraper(web)
                        extracted_info = extract_info(scraped_content, extraction_prompt)
                        single = enhanced_json_extractor(extracted_info)
                        
                        # Convert the result to a DataFrame
                        single_df = single_to_dataframe(single)
                        
                        if single_df is not None and not single_df.empty:
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
                            
                            sub_status.success(f"Extracted {len(single_df)} records from {web}")
                        else:
                            sub_status.warning(f"No data extracted from {web}")
                    
                    except Exception as e:
                        sub_status.error(f"Error processing website {web}: {str(e)}")
                    
                    # Update progress
                    progress_bar.progress((i + 1) / len(websites))
                
                # Clear progress bar when done
                progress_bar.empty()
                status.success("Processing completed!")
                
                # Step 3: Display and save results
                if main_df is not None and not main_df.empty:
                    # Save to CSV file
                    main_df.to_csv(output_filename, index=False)
                    
                    # Display results
                    st.subheader("Scraped Data")
                    st.dataframe(main_df)
                    
                    # Create download button
                    csv_data = main_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=output_filename,
                        mime="text/csv",
                    )
                    
                    st.success(f"Data saved to {output_filename}")
                else:
                    st.warning("No data was extracted from any website.")
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)
    
    # Add sidebar with additional information
    with st.sidebar:
        st.header("About")
        st.info("""
        This application uses:
        - Website extraction to find URLs in text
        - Web scraping to collect data from websites
        - Information extraction with AI
        - CSV export for saving and sharing results
        """)
        


if __name__ == "__main__":
    streamlit_app()