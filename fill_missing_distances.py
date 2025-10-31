
import pandas as pd
import numpy as np

def fill_missing_distances():
    try:
        # Load the data file that has the 9 missing records
        df = pd.read_csv("patient_data_with_full_distances.csv")

        # Define the imputation values
        montana_avg_distance = 15.42
        imputation_name = "Estimated - Montana Average"

        # Find the rows where distance is missing
        missing_mask = df['distance_to_nearest_pharmacy'].isnull()
        num_missing = missing_mask.sum()

        if num_missing > 0:
            print(f"Found {num_missing} records with missing distance information. Proceeding with imputation.")

            # Impute the missing values
            df.loc[missing_mask, 'distance_to_nearest_pharmacy'] = montana_avg_distance
            df.loc[missing_mask, 'nearest_pharmacy_name'] = imputation_name
            # Ensure the other related columns are empty (NaN)
            df.loc[missing_mask, 'nearest_pharmacy_lat'] = np.nan
            df.loc[missing_mask, 'nearest_pharmacy_lon'] = np.nan

            # --- Save to New File ---
            output_filename = "patient_data_with_imputed_distances.csv"
            df.to_csv(output_filename, index=False)
            print(f"\nSuccessfully imputed missing values and saved the final data to '{output_filename}'")
            
            # --- Final Verification ---
            final_missing = df['distance_to_nearest_pharmacy'].isnull().sum()
            if final_missing == 0:
                print("Verification successful: There are no more missing distance values in the new file.")
            else:
                print(f"Verification failed: Still found {final_missing} missing distance values.")

        else:
            print("No missing distance values found. No imputation needed.")

    except FileNotFoundError:
        print("Error: 'patient_data_with_full_distances.csv' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fill_missing_distances()
