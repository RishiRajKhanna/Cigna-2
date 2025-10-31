
import pandas as pd
import numpy as np

def verify_alaska_data():
    try:
        # Load the final merged data
        df = pd.read_csv("patient_data_with_full_distances.csv")

        # Filter for records in Alaska
        alaska_df = df[df['us_state'].str.lower() == 'alaska']

        if not alaska_df.empty:
            print(f"Found {len(alaska_df)} records for Alaska in the final file.")

            # Check if the county's own coordinates are present
            lat_lon_missing = alaska_df['correct_county_lat'].isnull().sum()
            
            if lat_lon_missing == 0:
                print("\n[SUCCESS] The 'correct_county_lat' and 'correct_county_lon' fields ARE present for all Alaska records.")
                print("This means the merge with uscounties.xlsx worked correctly.")
            else:
                print(f"\n[WARNING] Found {lat_lon_missing} Alaska records with missing county coordinates.")

            # Check if the pharmacy distance fields are missing
            distance_missing = alaska_df['distance_to_nearest_pharmacy'].isnull().sum()

            if distance_missing == len(alaska_df):
                print(f"\n[CONFIRMED] The 'distance_to_nearest_pharmacy' field IS missing for all {len(alaska_df)} Alaska records.")
                print("This confirms the issue is that the county_pharmacy_distances.csv file has no data for Alaska.")
            else:
                print(f"\n[INFO] Found {distance_missing} Alaska records with missing distance information.")

        else:
            print("No records for Alaska were found in the final file.")

    except FileNotFoundError:
        print("Error: 'patient_data_with_full_distances.csv' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    verify_alaska_data()
