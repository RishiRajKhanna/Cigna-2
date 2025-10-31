
import pandas as pd

def inspect_merged_data():
    try:
        # Load the merged data
        df = pd.read_csv("patient_data_with_full_distances.csv")

        # Filter for rows where the merge likely failed
        unmatched_df = df[df['distance_to_nearest_pharmacy'].isnull()]

        if not unmatched_df.empty:
            print(f"Found {len(unmatched_df)} rows with empty distance fields.")
            print("This is because these counties could not be matched between the patient data and the county distance file.")
            
            # Display the unique county/state combinations that failed to match
            unmatched_counties = unmatched_df[['us_county', 'us_state']].drop_duplicates().sort_values(by=['us_state', 'us_county'])
            
            print("\nHere are the unique county and state combinations that could not be matched:")
            print(unmatched_counties.to_string(index=False))

        else:
            print("No rows with empty distance fields were found.")

    except FileNotFoundError:
        print("Error: 'patient_data_with_full_distances.csv' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    inspect_merged_data()
