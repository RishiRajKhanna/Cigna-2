
import pandas as pd

def merge_data():
    try:
        # Load the patient data
        patient_df = pd.read_csv("synthetic_patient_data_with_distances.csv")
        print("Successfully loaded patient data.")

        # Load the new county coordinates data from the Excel file
        coords_df = pd.read_excel("uscounties.xlsx")
        print("Successfully loaded county coordinates data from uscounties.xlsx.")

        # --- Data Preparation for Merging ---
        # 1. Prepare coords_df:
        # Select and rename columns to be more explicit
        coords_df = coords_df[['county', 'state_name', 'lat', 'lng']]
        coords_df.rename(columns={
            'county': 'us_county',
            'state_name': 'us_state',
            'lat': 'correct_county_lat',
            'lng': 'correct_county_lon'
        }, inplace=True)

        # 2. Standardize join keys in both dataframes
        # Function to clean county names for better matching
        def clean_county_name(county_name):
            if isinstance(county_name, str):
                county_name = county_name.lower().strip()
                # Remove common Alaskan suffixes
                county_name = county_name.replace(' borough', '')
                county_name = county_name.replace(' census area', '')
                county_name = county_name.replace(' municipality', '')
                county_name = county_name.replace(' city and borough', '')
                county_name = county_name.replace(' county', '') # Also remove ' county' for general consistency
            return county_name

        # Convert to string, strip whitespace, and convert to lowercase
        for df_obj in [patient_df, coords_df]:
            df_obj['us_county'] = df_obj['us_county'].astype(str).apply(clean_county_name)
            df_obj['us_state'] = df_obj['us_state'].astype(str).str.strip().str.lower()

        # --- Merging ---
        # Drop duplicates from coords_df to avoid creating extra rows in patient_df
        coords_df.drop_duplicates(subset=['us_county', 'us_state'], inplace=True)

        # Perform a left merge to keep all patient records
        merged_df = pd.merge(
            patient_df,
            coords_df,
            on=['us_county', 'us_state'],
            how='left'
        )
        print("Successfully merged the two dataframes.")

        # --- Verification ---
        null_coords_count = merged_df['correct_county_lat'].isnull().sum()
        if null_coords_count > 0:
            print(f"Warning: {null_coords_count} patient records could not be matched with the new county coordinates.")
            # Optional: To see which ones didn't match, you could uncomment the following lines
            # unmatched_rows = merged_df[merged_df['correct_county_lat'].isnull()]
            # print("Sample of unmatched rows:")
            # print(unmatched_rows[['us_county', 'us_state']].drop_duplicates().head())
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
