import pandas as pd
import re

def heuristic_filter():
    print("Loading master_app_list.csv...")
    df = pd.read_csv("master_app_list.csv")
    
    # Define strong signals for AI companion apps based on the prompt's definition
    companion_keywords = [
        r'\bboyfriend\b', r'\bgirlfriend\b', r'\bcompanion\b', 
        r'\bwaifu\b', r'\bhusbando\b', r'\broleplay\b', 
        r'\bvirtual friend\b', r'\bsoulmate\b', r'\bintimate\b', 
        r'\bromantic\b', r'\bai friend\b', r'\bchat with characters\b',
        r'\banime girl\b', r'\bvirtual partner\b'
    ]
    
    # Compile the keywords into a single regex pattern
    pattern = '|'.join(companion_keywords)
    
    print("Applying local offline heuristic filter...")
    
    # Filter: Keep rows where Title or Description contains the keywords (case insensitive)
    mask = df['Title'].str.contains(pattern, case=False, na=False) | \
           df['Description'].str.contains(pattern, case=False, na=False)
           
    filtered_df = df[mask]
    
    # Optional: Add the 'app_type' column to match the required CSV format
    filtered_df['app_type'] = 'companion' # Defaulting to companion for the matches
    
    print(f"\nFiltering complete! Reduced list from {len(df)} to {len(filtered_df)} target apps.")
    
    # Save the output
    filtered_df.to_csv("filtered_targets.csv", index=False)
    print("Saved to filtered_targets.csv. You bypassed the API limitation!")

if __name__ == "__main__":
    heuristic_filter()