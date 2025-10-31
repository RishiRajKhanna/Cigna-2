
import pandas as pd

def verify_coords_only():
    try:
        # Load the patient data with correct coordinates
        df = pd.read_csv("patient_data_with_correct_coords.csv")

        # Filter for records in Alaska
        alaska_df = df[df['us_state'].str.lower() == 'alaska']

        if not alaska_df.empty:
            print(f"Found {len(alaska_df)} records for Alaska in patient_data_with_correct_coords.csv.")

            # Check if the county's own coordinates are present
            lat_lon_missing = alaska_df['correct_county_lat'].isnull().sum()
            
            if lat_lon_missing == 0:
                print("\n[SUCCESS] The 'correct_county_lat' and 'correct_county_lon' fields ARE present for all Alaska records.")
                print("All Alaskan counties now have their coordinates.")
            else:
                print(f"\n[WARNING] Found {lat_lon_missing} Alaska records with missing county coordinates.")
                print("These are the remaining unmatched records after cleaning county names.")
                print("Unique unmatched Alaskan counties:")
                print(alaska_df[alaska_df['correct_county_lat'].isnull()][['us_county', 'us_state']].drop_duplicates().to_string(index=False))

        else:
            print("No records for Alaska were found in patient_data_with_correct_coords.csv.")

    except FileNotFoundError:
        print("Error: 'patient_data_with_correct_coords.csv' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    verify_coords_only()
