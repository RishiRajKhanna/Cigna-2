
import pandas as pd

def count_unique_counties():
    files_to_check = {
        "Original Patient Data": "synthetic_patient_data_with_distances.csv",
        "County-Pharmacy Distances": "county_pharmacy_distances.csv",
        "Final Imputed Patient Data": "patient_data_with_imputed_distances.csv"
    }

    print("--- Data Audit: Counting Unique Counties ---")

    for description, file_path in files_to_check.items():
        try:
            df = pd.read_csv(file_path)
            
            # Standardize column names for counting
            if 'us_county' in df.columns and 'us_state' in df.columns:
                county_col = 'us_county'
                state_col = 'us_state'
            elif 'county' in df.columns and 'state' in df.columns:
                county_col = 'county'
                state_col = 'state'
            else:
                print(f"\nCould not find standard county/state columns in: {file_path}")
                continue

            # Clean and count unique county-state pairs
            df[county_col] = df[county_col].astype(str).str.strip().str.lower()
            df[state_col] = df[state_col].astype(str).str.strip().str.lower()
            
            unique_count = len(df[[county_col, state_col]].drop_duplicates())
            
            print(f"\nFile: {file_path} ({description})")
            print(f"Number of unique counties: {unique_count}")

        except FileNotFoundError:
            print(f"\nFile not found: {file_path}")
        except Exception as e:
            print(f"\nAn error occurred while processing {file_path}: {e}")

if __name__ == "__main__":
    count_unique_counties()
