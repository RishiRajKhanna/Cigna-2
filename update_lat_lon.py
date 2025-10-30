
import pandas as pd

# Load the patient data
patient_data_path = "C:\\Users\\703401801\\Desktop\\Cigna\\synthetic_patient_data_processed.csv"
df = pd.read_csv(patient_data_path)

# Load the county data from the URL
county_data_url = "https://gist.githubusercontent.com/russellsamora/12be4f9f574e92413ea3f92ce1bc58e6/raw/us_county_latlng.csv"
county_df = pd.read_csv(county_data_url)

# Prepare for the merge
county_df.rename(columns={'name': 'us_county', 'lat': 'new_latitude', 'lng': 'new_longitude'}, inplace=True)

# Merge the dataframes
df = pd.merge(df, county_df, on='us_county', how='left')

# Update the latitude and longitude columns
# Only update where a match was found
df['latitude'] = df['new_latitude'].fillna(df['latitude'])
df['longitude'] = df['new_longitude'].fillna(df['longitude'])

# Drop the temporary columns
df.drop(columns=['fips_code', 'new_latitude', 'new_longitude'], inplace=True)

# Save the updated dataframe
df.to_csv(patient_data_path, index=False)

print(f"File updated successfully and saved to {patient_data_path}")
