import pandas as pd
from google import genai
import time

# The new SDK automatically detects the GEMINI_API_KEY environment variable
client = genai.Client()

# Using the most current, supported flash model for the new SDK
MODEL_ID = 'gemini-2.5-flash'

def classify_app(row):
    title = row['Title']
    description = str(row['Description'])
    
    prompt = f"""
    Analyze the following app based on its Title and Description. 
    Classify the app into exactly ONE of the following categories: 'companion', 'general_purpose', 'mixed', or 'other'.
    
    Definition:
    - 'companion': Markets itself around social or relational engagement (e.g., AI girlfriend/boyfriend, virtual friend, roleplay).
    - 'general_purpose': General-purpose LLMs (e.g., ChatGPT, Claude, Gemini, Copilot).
    - 'mixed': Offers both clear social/relational companion features AND general-purpose/task-based features.
    - 'other': Apps designed for specific tasks (homework, study, therapy, utility) or anything that doesn't fit the above.
    
    Title: {title}
    Description: {description[:1200]}
    
    Respond with ONLY the classification word (companion, general_purpose, mixed, or other). No other text.
    """
    
        try:
            # New SDK syntax for generating content
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
            )
            classification = response.text.strip().lower()
            
            # Clean up output
            if "companion" in classification: return "companion"
            if "general_purpose" in classification: return "general_purpose"
            if "mixed" in classification: return "mixed"
            return "other"
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "quota" in err_str.lower() or "exhausted" in err_str.lower():
                print(f"Rate limited on {title}. Retrying in 30s... ({attempt+1}/{max_retries})")
                time.sleep(30)
            else:
                print(f"Error on {title}: {e}")
                return "error"
    print(f"Max retries exceeded for {title}")
    return "error"

def process_data():
    print("Loading master_app_list.csv...")
    df = pd.read_csv("master_app_list.csv")
    
    print(f"Loaded {len(df)} apps. Starting sequential AI classification...")
    
    results = []
    
    # Iterate sequentially with a delay to respect the 15 RPM free-tier limit
    for i, row in df.iterrows():
        result = classify_app(row)
        results.append(result)
        
        time.sleep(4) 
        
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/{len(df)} apps...")
            
    df['app_type'] = results
    
    # The Magic Filter: Drop everything that isn't a companion or mixed app
    filtered_df = df[df['app_type'].isin(['companion', 'mixed'])]
    
    print(f"\nClassification complete! Reduced list from {len(df)} to {len(filtered_df)} target apps.")
    
    # Save the output
    filtered_df.to_csv("filtered_targets.csv", index=False)
    print("Saved to filtered_targets.csv")

if __name__ == "__main__":
    process_data()