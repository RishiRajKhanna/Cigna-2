
import pandas as pd
import numpy as np
from geopy.distance import geodesic

# Load the full patient data
patient_data_path = "C:\\Users\\703401801\\Desktop\\Cigna\\synthetic_patient_data_processed.csv"
df = pd.read_csv(patient_data_path)

# Load the county data from the URL
county_data_url = "https://gist.githubusercontent.com/russellsamora/12be4f9f574e92413ea3f92ce1bc58e6/raw/us_county_latlng.csv"
county_df = pd.read_csv(county_data_url)
county_df.rename(columns={'name': 'county', 'lat': 'latitude', 'lng': 'longitude'}, inplace=True)

# Realistic simulation of pharmacy data
np.random.seed(42)
population_log_normal = np.random.lognormal(mean=10, sigma=1.5, size=len(county_df))
county_df['population'] = population_log_normal.astype(int)
pharmacies_per_10k_rate = np.random.uniform(1.5, 3.5, size=len(county_df))
county_df['pharmacy_count'] = ((county_df['population'] / 10000) * pharmacies_per_10k_rate + np.random.randint(-2, 3, size=len(county_df))).astype(int)
county_df['pharmacy_count'] = county_df['pharmacy_count'].clip(lower=0)
county_df['pharmacies_per_10k'] = (county_df['pharmacy_count'] / county_df['population']) * 10000
county_df['is_pharmacy_desert'] = county_df['pharmacies_per_10k'] < 1

non_desert_counties = county_df[county_df['is_pharmacy_desert'] == False]

def find_nearest_non_desert(patient_county):
    try:
        patient_geo = county_df[county_df['county'] == patient_county]
        if patient_geo.empty:
            return "County not found in dataset"
        patient_coords = (patient_geo.iloc[0]['latitude'], patient_geo.iloc[0]['longitude'])
        
        distances = [
            (geodesic(patient_coords, (row.latitude, row.longitude)).km, row.county)
            for row in non_desert_counties.itertuples()
        ]
        
        if not distances:
            return "No non-desert counties found"
            
        min_distance, nearest_county = min(distances, key=lambda x: x[0])
        return nearest_county
    except Exception as e:
        return f"Error: {e}"

print("Processing the full file. This may take a few minutes...")
df['nearest_non_desert_county'] = df['us_county'].apply(find_nearest_non_desert)

# Save the updated dataframe to a new file
output_path = "C:\\Users\\703401801\\Desktop\\Cigna\\synthetic_patient_data_with_nearest_non_desert.csv"
df.to_csv(output_path, index=False)

print(f"Processing complete. File saved to {output_path}")
