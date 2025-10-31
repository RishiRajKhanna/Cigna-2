
import pandas as pd

def count_pharmacy_deserts():
    try:
        # Load the final, imputed dataset
        df = pd.read_csv("patient_data_with_imputed_distances.csv")

        # Define the pharmacy desert threshold
        desert_threshold = 20  # miles

        # Filter for records where the distance is >= the threshold
        desert_df = df[df['distance_to_nearest_pharmacy'] >= desert_threshold]

        if not desert_df.empty:
            # Get the number of unique counties that are deserts
            unique_desert_counties = desert_df[['us_county', 'us_state']].drop_duplicates()
            num_desert_counties = len(unique_desert_counties)

            print(f"Based on the 20-mile rule, there are {num_desert_counties} unique pharmacy desert counties in the final dataset.")
            
            print("\nHere are the desert counties found:")
            # Sort for consistent output
            unique_desert_counties = unique_desert_counties.sort_values(by=['us_state', 'us_county'])
            print(unique_desert_counties.to_string(index=False))

        else:
            print("No pharmacy desert counties found in the final dataset.")

    except FileNotFoundError:
        print("Error: 'patient_data_with_imputed_distances.csv' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    count_pharmacy_deserts()
