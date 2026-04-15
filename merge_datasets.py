import csv
import os

# Read the pilot dataset
pilot_rows = []
with open('final_evaluation_dataset_pilot.csv', 'r', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        pilot_rows.append(row)

# Read the batch2 dataset if it exists
batch2_rows = []
batch2_file = 'final_evaluation_dataset_batch2.csv'
if os.path.exists(batch2_file):
    with open(batch2_file, 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            batch2_rows.append(row)

# Merge: pilot first, then batch2
merged_rows = pilot_rows + batch2_rows

# Save as final
with open('final_app_evaluation_dataset.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(merged_rows)

print("Merged dataset saved as final_app_evaluation_dataset.csv")