import pandas as pd
import os
import json
import sys

def update_csv(app_title, data):
    # Only read the first 30 rows to avoid parsing issues further down the file
    master_df = pd.read_csv('filtered_targets.csv', nrows=30)
    
    # Attempt to find the specific app
    matches = master_df[master_df['Title'] == app_title]
    if len(matches) == 0:
        print(f"Error: Could not find '{app_title}' in the first 30 rows.")
        return
        
    row = matches.iloc[0]
    
    # Merge existing data (Title, Description, app_type) and new data
    new_row = {
        'Title': row['Title'],
        'Description': row['Description'],
        'app_type': row['app_type']
    }
    new_row.update(data)
    
    csv_file = 'final_evaluation_dataset_pilot.csv'
    
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        # remove existing entry if present to update
        df = df[df['Title'] != app_title]
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df = pd.DataFrame([new_row])
        
    df.to_csv(csv_file, index=False)
    print(f"Successfully updated record for: {app_title}")

if __name__ == "__main__":
    app_title = sys.argv[1]
    data = json.loads(sys.argv[2])
    update_csv(app_title, data)
