
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist

def haversine_distance(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 3956 # Radius of Earth in miles
    return c * r

def calculate_nearest_pharmacy():
    try:
        # Load the patient data with correct coordinates
        patient_df = pd.read_csv("patient_data_with_correct_coords.csv")
        print("Successfully loaded patient data with correct coordinates.")

        # Load the pharmacy data
        pharmacy_df = pd.read_csv("Pharmacies.csv")
        print("Successfully loaded pharmacy data.")

        # --- Data Preparation ---
        # Get unique county coordinates
        county_coords = patient_df[['us_county', 'us_state', 'correct_county_lat', 'correct_county_lon']].drop_duplicates().dropna()

        # Prepare pharmacy coordinates
        pharmacy_coords = pharmacy_df[['Y', 'X']].dropna()

        # --- Distance Calculation ---
        # Do not convert to radians here, the haversine function will do it.
        county_deg = county_coords[['correct_county_lat', 'correct_county_lon']].values
        pharmacy_deg = pharmacy_coords[['Y', 'X']].values

        # Use a more efficient haversine implementation for cdist
        dist_matrix = cdist(county_deg, pharmacy_deg, lambda u, v: haversine_distance(v[1], v[0], u[1], u[0]))

        # Find the minimum distance for each county
        min_distances = dist_matrix.min(axis=1)
        nearest_pharmacy_indices = dist_matrix.argmin(axis=1)

        # --- Create Final DataFrame ---
        results_df = county_coords.copy()
        results_df['distance_to_nearest_pharmacy'] = min_distances
        
        # Get the details of the nearest pharmacy
        nearest_pharmacies = pharmacy_df.iloc[nearest_pharmacy_indices]
        results_df['nearest_pharmacy_name'] = nearest_pharmacies['NAME'].values
        results_df['nearest_pharmacy_lat'] = nearest_pharmacies['Y'].values
        results_df['nearest_pharmacy_lon'] = nearest_pharmacies['X'].values

        # --- Save to New File ---
        output_filename = "county_pharmacy_distances.csv"
        results_df.to_csv(output_filename, index=False)
        print(f"Successfully saved the distance calculations to '{output_filename}'")

    except FileNotFoundError as e:
        print(f"Error: A required file was not found. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    calculate_nearest_pharmacy()
