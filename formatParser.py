import pandas as pd

def save_to_csv(data,
                output_file='output.csv'):
    """
    Save data to a CSV file
    
    Args:
        data: A dictionary containing data to be saved. Can be either:
              - A dictionary with one key containing a list of dictionaries
              - A single dictionary with key-value pairs
        output_file: Name of the output CSV file
    """
    # Handle different data structures
    if isinstance(data, dict):
        if len(data) == 1 and isinstance(list(data.values())[0], list):
            # Case 1: Dictionary with one key containing a list of dictionaries
            key = list(data.keys())[0]
            data_list = data[key]
            
            # Convert the list of dictionaries to a DataFrame
            df = pd.DataFrame(data_list)
        else:
            # Case 2: Single dictionary with key-value pairs
            # Convert the dictionary to a DataFrame with a single row
            df = pd.DataFrame([data])
    else:
        raise ValueError("Input data must be a dictionary")
    
    # Save as CSV file
    df.to_csv(output_file,
              index=False,
              encoding='utf-8')
    print(f"Data has been saved to {output_file}")
