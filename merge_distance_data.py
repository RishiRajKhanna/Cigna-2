
import pandas as pd

def merge_distance_data():
    try:
        # Load the patient data with correct coordinates
        patient_df = pd.read_csv("patient_data_with_correct_coords.csv")
        print("Successfully loaded patient_data_with_correct_coords.csv")

        # Load the county pharmacy distances data
        distances_df = pd.read_csv("county_pharmacy_distances.csv")
        print("Successfully loaded county_pharmacy_distances.csv")

        # --- Data Preparation for Merging ---
        # Select only the required columns from the distances_df
        distance_columns = [
            'us_county', 'us_state', 'distance_to_nearest_pharmacy',
            'nearest_pharmacy_name', 'nearest_pharmacy_lat', 'nearest_pharmacy_lon'
        ]
        distances_to_merge = distances_df[distance_columns]

        # Standardize join keys in both dataframes for a robust merge
        for df in [patient_df, distances_to_merge]:
            df['us_county'] = df['us_county'].astype(str).str.strip().str.lower()
            df['us_state'] = df['us_state'].astype(str).str.strip().str.lower()

        # --- Merging ---
        # Perform a left merge to keep all patient records and add the distance info
        merged_df = pd.merge(
            patient_df,
            distances_to_merge,
            on=['us_county', 'us_state'],
            how='left'
        )
        print("Successfully merged the distance data into the patient data.")

        # --- Verification ---
        # Check for any rows that were not successfully merged
        unmerged_count = merged_df['distance_to_nearest_pharmacy'].isnull().sum()
        if unmerged_count > 0:
            print(f"Warning: {unmerged_count} patient records could not be matched with a county distance.")
        else:
            print("All patient records were successfully updated with pharmacy distance information.")

        # --- Save to New File ---
        output_filename = "patient_data_with_full_distances.csv"
        merged_df.to_csv(output_filename, index=False)
        print(f"Successfully saved the final merged data to '{output_filename}'")

    except FileNotFoundError as e:
        print(f"Error: A required file was not found. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    merge_distance_data()
