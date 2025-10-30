
import pandas as pd

file_path = r"C:\Users\703401801\Desktop\Cigna\synthetic_patient_data.csv"

try:
    df = pd.read_csv(file_path)

    if 'proposed_pharmacy_location_us_county' in df.columns:
        # Group by the proposed county and count the number of patients in each
        patient_counts = df.groupby('proposed_pharmacy_location_us_county').size().reset_index(name='number_of_patients')
        
        print("--- Patient Count per Proposed Pharmacy Location ---")
        print(patient_counts.to_string())
    else:
        print("Error: The column 'proposed_pharmacy_location_us_county' was not found in the file.")

except FileNotFoundError:
    print(f"Error: The file at {file_path} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
