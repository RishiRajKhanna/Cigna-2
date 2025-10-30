
import pandas as pd

file_path = "synthetic_patient_data_with_distances.csv"

try:
    df = pd.read_csv(file_path)
    
    # Check if 'cluster' column exists
    if 'cluster' in df.columns:
        missing_clusters = df['cluster'].isnull().sum()
        if missing_clusters > 0:
            print(f"Found {missing_clusters} patients with no cluster allocation.")
            # Displaying a few rows where the cluster is missing
            print("Here are some of the rows with missing data:")
            print(df[df['cluster'].isnull()].head())
        else:
            print("No patients with missing cluster allocations were found. All rows seem to be populated.")
    else:
        print("The 'cluster' column does not exist in the file.")

except FileNotFoundError:
    print(f"Error: The file at {file_path} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
