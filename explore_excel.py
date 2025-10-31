
import pandas as pd

def explore_excel_file():
    try:
        # Load the Excel file
        df = pd.read_excel("uscounties.xlsx")
        
        # Print the column names
        print("--- Column Names ---")
        print(df.columns.tolist())
        
        # Print the first 5 rows of the dataframe
        print("\n--- First 5 Rows ---")
        print(df.head())

    except FileNotFoundError:
        print("Error: 'uscounties.xlsx' not found. Please make sure the file is in the correct directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    explore_excel_file()
