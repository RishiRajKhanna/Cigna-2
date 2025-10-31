
import pandas as pd

def merge_data():
    try:
        # Load the patient data
        patient_df = pd.read_csv("synthetic_patient_data_with_distances.csv")
        print("Successfully loaded patient data.")

        # Load the county coordinates data
        coords_df = pd.read_csv("county_coordinates.csv")
        print("Successfully loaded county coordinates data.")

        # --- Data Preparation for Merging ---
        # 1. Clean up coords_df:
        # Drop unnamed columns that appear due to trailing commas
        coords_df = coords_df.loc[:, ~coords_df.columns.str.contains('^Unnamed')]
        # Rename columns to be more explicit and lowercase for consistency
        coords_df.rename(columns={
            'County': 'us_county',
            'State': 'us_state',
            'Latitude': 'correct_county_lat',
            'Longitude': 'correct_county_lon'
        }, inplace=True)

        # 2. Standardize join keys in both dataframes
        # Convert to string, strip whitespace, and convert to lowercase
        for df in [patient_df, coords_df]:
            df['us_county'] = df['us_county'].astype(str).str.strip().str.lower()
            df['us_state'] = df['us_state'].astype(str).str.strip().str.lower()

        # --- Merging ---
        # Perform a left merge to keep all patient records
        # and add the new coordinates where a match is found.
        merged_df = pd.merge(
            patient_df,
            coords_df,
            on=['us_county', 'us_state'],
            how='left'
        )
        print("Successfully merged the two dataframes.")

        # --- Verification ---
        # Check how many rows have nulls for the new coordinates
        null_coords_count = merged_df['correct_county_lat'].isnull().sum()
        if null_coords_count > 0:
            print(f"Warning: {null_coords_count} patient records could not be matched with new county coordinates.")
            print("This might be due to differences in county or state names between the two files.")
        else:
            print("All patient records were successfully matched with new county coordinates.")

        # --- Save to New File ---
        output_filename = "patient_data_with_correct_coords.csv"
        merged_df.to_csv(output_filename, index=False)
        print(f"Successfully saved the merged data to '{output_filename}'")

    except FileNotFoundError as e:
        print(f"Error: A required file was not found. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    merge_data()
