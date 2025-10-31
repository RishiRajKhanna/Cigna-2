
import pandas as pd

def inspect_distances():
    try:
        df = pd.read_csv("county_pharmacy_distances.csv")
        
        if 'distance_to_nearest_pharmacy' in df.columns:
            max_distance = df['distance_to_nearest_pharmacy'].max()
            print(f"The maximum distance to a nearest pharmacy is: {max_distance:.2f} miles.")
            
            # Also, let's see how many are close to the threshold
            close_to_threshold = df[df['distance_to_nearest_pharmacy'] >= 15]
            print(f"There are {len(close_to_threshold)} counties with a distance of 15 miles or more.")
        else:
            print("Error: 'distance_to_nearest_pharmacy' column not found in the file.")

    except FileNotFoundError:
        print("Error: 'county_pharmacy_distances.csv' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    inspect_distances()
