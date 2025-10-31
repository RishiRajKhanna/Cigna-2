
import pandas as pd

def calculate_average_distances():
    try:
        # Load the county pharmacy distances data
        df = pd.read_csv("county_pharmacy_distances.csv")

        # Calculate the average distance for Montana
        montana_avg_distance = df[df['us_state'].str.lower() == 'montana']['distance_to_nearest_pharmacy'].mean()

        if pd.notna(montana_avg_distance):
            print(f"The average distance to the nearest pharmacy in Montana is: {montana_avg_distance:.2f} miles.")
        else:
            print("Could not calculate the average distance for Montana.")

    except FileNotFoundError:
        print("Error: 'county_pharmacy_distances.csv' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    calculate_average_distances()
