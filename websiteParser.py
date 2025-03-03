import os
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import (BaseModel,
                      Field)
load_dotenv(override=True)

class WebsiteInfo(BaseModel):
    urls: List[str] = Field(description="A list of URLs")

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_websites(text: str):
    """
    Extract all websites/URLs from the provided text using OpenAI parse method.
    
    Args:
        text (str): Input text containing website URLs
        
    Returns:
        The parsed response or refusal message
    """
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant specialized in extracting URLs and websites from text."
            },
            {"role": "user", "content": f"Extract all websites from this text:\n\n{text}"}
        ],
        response_format=WebsiteInfo,
    )
    
    website_info = completion.choices[0].message
    # If the model refuses to respond, you will get a refusal message
    if hasattr(website_info, 'refusal') and website_info.refusal:
        print(website_info.refusal)
        return None
    else:
        return website_info.parsed.urls

# Example usage
if __name__ == "__main__":
    sample_text = """Here are some websites:
    Check out https://www.example.com for more information.
    You can also visit github.com or read the documentation at https://docs.python.org/3/.
    For academic research, try scholar.google.com.
    """
    
    result = extract_websites(sample_text)
    print(result)