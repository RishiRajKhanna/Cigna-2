
import pandas as pd

def format_county_names():
    try:
        # Load the final dataset
        file_path = "patient_data_with_imputed_distances.csv"
        df = pd.read_csv(file_path)

        # Convert 'us_county' and 'us_state' to title case
        # Ensure they are strings before applying .title()
        df['us_county'] = df['us_county'].astype(str).apply(lambda x: x.title())
        df['us_state'] = df['us_state'].astype(str).apply(lambda x: x.title())

        # Save the modified DataFrame, overwriting the original file
        df.to_csv(file_path, index=False)
        print(f"Successfully formatted 'us_county' and 'us_state' to title case in {file_path}")

    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    format_county_names()
