import streamlit as st
import pandas as pd
from scraper import firecrawl_scraper
from websiteParser import extract_websites
from formatParser import save_to_csv
import os

def main():
    """
    Streamlit application that provides a UI for the web scraping functionality
    from the original main.py file.
    """
    # App title and description
    st.title("Web Scraping agent")
    st.markdown("""
    This app helps you extract website URLs from text, scrape content from these websites,
    and save the results to a CSV file.
    
    **Instructions:**
    1. Enter text containing website URLs in the text area below
    2. Click 'Process' to start the extraction and scraping process
    3. View the results and download the CSV file
    
    **Example:**
    ```
    Please scrape https://www.creative-biolabs.com/search.aspx?key=Anapoe&ty=tag and extract all products with their Molecular Formula.
    ```
    """)
    
    # User input text area
    user_input = st.text_area("Enter your text containing website URLs:", 
                             height=150,
                             help="Enter text that includes website URLs. This text will also serve as the prompt for scraping.",
                             placeholder="Example: Please scrape https://www.creative-biolabs.com/search.aspx?key=Anapoe&ty=tag and extract all products with their Molecular Formula.")
    
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
                
                # Step 2: Scrape websites
                status.info("Scraping data from websites. This may take a while...")
                
                # Use the scraper to get distributors data
                distributors = firecrawl_scraper(websites, prompt=user_input)
                
                # Update status
                status.success("Scraping completed!")
                
                # Step 3: Display results
                st.subheader("Scraped Data")
                
                # Convert to DataFrame for display
                if distributors:
                    df = pd.DataFrame(distributors)
                    st.dataframe(df)
                    
                    # Step 4: Save to CSV
                    save_to_csv(distributors)
                    
                    # Find the CSV file that was created
                    # Note: This assumes save_to_csv saves to the current directory
                    # You may need to adjust this if your save_to_csv function uses a different path
                    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
                    latest_csv = max(csv_files, key=os.path.getctime) if csv_files else None
                    
                    if latest_csv:
                        # Read the saved file to provide download capability
                        with open(latest_csv, 'rb') as f:
                            csv_data = f.read()
                        
                        # Provide download link
                        st.download_button(
                            label="Download CSV",
                            data=csv_data,
                            file_name=latest_csv,
                            mime='text/csv'
                        )
                else:
                    st.warning("No data was scraped from the websites.")
            
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
        - CSV export for saving and sharing results
        """)
        
        st.header("Example Usage")
        st.info("""
        **Example:**
        
        To scrape product information from Creative BioLabs, enter:
        
        "Please scrape https://www.creative-biolabs.com/search.aspx?key=Anapoe&ty=tag and extract all products with their Molecular Formula."
        
        This will extract all Anapoe products and their molecular formulas from the website.
        """)

if __name__ == "__main__":
    main()