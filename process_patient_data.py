import pandas as pd
import numpy as np
from geopy.distance import geodesic

# Load the patient data
patient_data_path = "C:\\Users\\703401801\\Desktop\\Cigna\\synthetic_patient_data_processed.csv"
df = pd.read_csv(patient_data_path)

# Step 1: Remove original pharmacy columns
df.drop(columns=['original_nearest_pharmacy', 'original_distance_to_pharmacy_km'], inplace=True)

# Step 2: Align drug_needs with medical_history
drug_mapping = {
    'Hypertension': 'Blood Pressure Medication',
    'Arthritis': 'Painkillers',
    'Asthma': 'Asthma Inhaler',
    'Diabetes': 'Insulin',
    'High Cholesterol': 'Statins',
    'Depression': 'Antidepressants'
}

def get_drug_need(medical_history):
    try:
        illnesses = eval(medical_history)
        for illness in illnesses:
            if illness in drug_mapping:
                return drug_mapping[illness]
    except:
        pass
    return "Unknown"

df['drug_needs'] = df['medical_history'].apply(get_drug_need)

# For steps 3, 4, and 5, we need external data.
# I will attempt to fetch a county dataset from a public source.
try:
    county_data_url = "https://raw.githubusercontent.com/grammakov/USA-cities-and-states/master/us_cities_states_counties.csv"
    # Try to read the CSV with error handling for bad lines
    county_df = pd.read_csv(county_data_url, on_bad_lines='skip')
    # This file is at the city level, so I'll aggregate to the county level
    county_geo = county_df.groupby(['county', 'state_id'])[[ 'latitude', 'longitude']].mean().reset_index()
except Exception as e:
    print(f"Error fetching county data: {e}")
    print("Even with error handling, I could not read the county data. I cannot proceed without this data.")
    exit()

# Realistic simulation of pharmacy data
np.random.seed(42)
# Simulate population with a log-normal distribution for a more realistic spread
population_log_normal = np.random.lognormal(mean=10, sigma=1.5, size=len(county_geo))
county_geo['population'] = population_log_normal.astype(int)

# Simulate pharmacy count based on population, with some noise
pharmacies_per_10k_rate = np.random.uniform(1.5, 3.5, size=len(county_geo))
county_geo['pharmacy_count'] = ((county_geo['population'] / 10000) * pharmacies_per_10k_rate + np.random.randint(-2, 3, size=len(county_geo))).astype(int)
county_geo['pharmacy_count'] = county_geo['pharmacy_count'].clip(lower=0)

county_geo['pharmacies_per_10k'] = (county_geo['pharmacy_count'] / county_geo['population']) * 10000
county_geo['is_pharmacy_desert'] = county_geo['pharmacies_per_10k'] < 1

non_desert_counties = county_geo[county_geo['is_pharmacy_desert'] == False]

def find_nearest_non_desert(patient_county, patient_state_short):
    try:
        patient_geo = county_geo[(county_geo['county'] == patient_county) & (county_geo['state_id'] == patient_state_short)]
        if patient_geo.empty:
            return None, None
        patient_coords = (patient_geo.iloc[0]['latitude'], patient_geo.iloc[0]['longitude'])
        
        distances = [
            (geodesic(patient_coords, (row.latitude, row.longitude)).km, row.county)
            for row in non_desert_counties.itertuples()
        ]
        
        if not distances:
            return None, None
            
        min_distance, nearest_county = min(distances, key=lambda x: x[0])
        return nearest_county, min_distance
    except:
        return None, None

# This part will be slow
# Create a mapping for us_state to state_id
state_mapping_full_to_short = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}
df['state_short'] = df['us_state'].map(state_mapping_full_to_short)

nearest_info = df.apply(lambda row: find_nearest_non_desert(row['us_county'], row['state_short']), axis=1)
df[['nearest_non_desert_county', 'distance_to_nearest_non_desert_county_km']] = pd.DataFrame(nearest_info.tolist(), index=df.index)

# Step 5: Update longitude and latitude
df = pd.merge(df, county_geo, left_on=['us_county', 'state_short'], right_on=['county', 'state_id'], how='left', suffixes=['', '_correct'])

df['latitude'] = df['latitude_correct']
df['longitude'] = df['longitude_correct']
df.drop(columns=['latitude_correct', 'longitude_correct', 'county', 'state_id', 'pharmacy_count', 'population', 'pharmacies_per_10k', 'is_pharmacy_desert', 'state_short'], inplace=True)

# Save the updated dataframe
output_path = "C:\\Users\\703401801\\Desktop\\Cigna\\synthetic_patient_data_processed_v2.csv"
df.to_csv(output_path, index=False)

print(f"File saved to {output_path}")