
import pandas as pd

def find_unmatched_counties():
    try:
        patient_df = pd.read_csv("synthetic_patient_data_with_distances.csv")
        coords_df = pd.read_csv("county_coordinates.csv")

        # Standardize column names and values for comparison
        coords_df.rename(columns={'County': 'us_county', 'State': 'us_state'}, inplace=True)
        
        patient_df['us_county_lower'] = patient_df['us_county'].astype(str).str.strip().str.lower()
        patient_df['us_state_lower'] = patient_df['us_state'].astype(str).str.strip().str.lower()
        
        coords_df['us_county_lower'] = coords_df['us_county'].astype(str).str.strip().str.lower()
        coords_df['us_state_lower'] = coords_df['us_state'].astype(str).str.strip().str.lower()

        # Create unique identifiers for each county/state pair
        patient_locations = set(zip(patient_df['us_county_lower'], patient_df['us_state_lower']))
        coords_locations = set(zip(coords_df['us_county_lower'], coords_df['us_state_lower']))

        # Find the locations that are in the patient data but not in the coordinates data
        unmatched_locations = sorted(list(patient_locations - coords_locations))

        if unmatched_locations:
            print("--- Unmatched County, State Pairs ---")
            for county, state in unmatched_locations:
                print(f"- County: {county}, State: {state}")
            print(f"\nFound {len(unmatched_locations)} unique unmatched county/state combinations.")
        else:
            print("All county/state pairs were successfully matched!")

    except FileNotFoundError as e:
        print(f"Error: A required file was not found. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    find_unmatched_counties()
