import pandas as pd
import os
import json
import sys
import csv

def update_csv(app_title, data):
    try:
        # Read the master list to get Title, Description, app_type
        master_df = None
        with open('filtered_targets.csv', 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if row[0] == app_title:
                    master_df = row
                    break
        
        if not master_df:
            print(f"Error: Could not find '{app_title}'")
            return
            
        new_row = {
            'Title': master_df[0],
            'Description': master_df[1],
            'app_type': master_df[3]
        }
        new_row.update(data)
        
        csv_file = 'final_evaluation_dataset_batch2.csv'
        
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            df = df[df['Title'] != app_title]
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])
            
        df.to_csv(csv_file, index=False)
        print(f"Successfully updated record for: {app_title}")
    except Exception as e:
        print(f"Error updating CSV: {e}")

if __name__ == "__main__":
    app_title = sys.argv[1]
    data = json.loads(sys.argv[2])
    update_csv(app_title, data)
