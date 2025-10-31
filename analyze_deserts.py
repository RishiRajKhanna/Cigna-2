
import pandas as pd

def analyze_deserts():
    try:
        df = pd.read_csv("county_pharmacy_distances.csv")
        
        if 'distance_to_nearest_pharmacy' in df.columns:
            # Filter for pharmacy deserts (distance >= 20 miles)
            desert_counties = df[df['distance_to_nearest_pharmacy'] >= 20]
            
            num_desert_counties = len(desert_counties)
            
            print(f"Based on the 20-mile rule, there are {num_desert_counties} pharmacy desert counties in the dataset.")
            
            if num_desert_counties > 0:
                print("\nHere are the pharmacy desert counties found:")
                print(desert_counties[['us_county', 'us_state', 'distance_to_nearest_pharmacy']].to_string(index=False))
        else:
            print("Error: 'distance_to_nearest_pharmacy' column not found in the file.")

    except FileNotFoundError:
        print("Error: 'county_pharmacy_distances.csv' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    analyze_deserts()
