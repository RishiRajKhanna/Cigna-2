# Analysis Scripts and Prompts

This document contains a summary of the major Python scripts created to generate and analyze the synthetic patient dataset.

## 1. Data Generation Script

**Prompt:** *A summary of the user's initial request to create a 5000-row synthetic patient dataset with specific columns, including real US county data, and additional synthetic health-related variables.*

This script generates the initial dataset with all patient attributes, including FIPS codes, ethnicity, and other features that were added in subsequent updates.

```python
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# County data collected from web searches with FIPS codes
county_data = [
    # California
    {'county': 'Calaveras County', 'state': 'California', 'latitude': 38.1839, 'longitude': -120.5614, 'FIPS_STATE_CODE': '06', 'county_fips_code': '06009'},
    {'county': 'Kings County', 'state': 'California', 'latitude': 36.0725, 'longitude': -119.8155, 'FIPS_STATE_CODE': '06', 'county_fips_code': '06031'},
    {'county': 'Los Angeles County', 'state': 'California', 'latitude': 34.1964, 'longitude': -118.2619, 'FIPS_STATE_CODE': '06', 'county_fips_code': '06037'},
    {'county': 'Marin County', 'state': 'California', 'latitude': 38.0769, 'longitude': -122.7227, 'FIPS_STATE_CODE': '06', 'county_fips_code': '06041'},
    {'county': 'Placer County', 'state': 'California', 'latitude': 39.0620, 'longitude': -120.7227, 'FIPS_STATE_CODE': '06', 'county_fips_code': '06061'},
    # Texas
    {'county': 'Anderson County', 'state': 'Texas', 'latitude': 31.8133, 'longitude': -95.6526, 'FIPS_STATE_CODE': '48', 'county_fips_code': '48001'},
    {'county': 'Andrews County', 'state': 'Texas', 'latitude': 32.2990, 'longitude': -102.5083, 'FIPS_STATE_CODE': '48', 'county_fips_code': '48003'},
    {'county': 'Angelina County', 'state': 'Texas', 'latitude': 31.2600, 'longitude': -94.6100, 'FIPS_STATE_CODE': '48', 'county_fips_code': '48005'},
    {'county': 'Aransas County', 'state': 'Texas', 'latitude': 28.0761, 'longitude': -96.9639, 'FIPS_STATE_CODE': '48', 'county_fips_code': '48007'},
    {'county': 'Archer County', 'state': 'Texas', 'latitude': 33.6153, 'longitude': -98.6877, 'FIPS_STATE_CODE': '48', 'county_fips_code': '48009'},
    # Florida
    {'county': 'Alachua County', 'state': 'Florida', 'latitude': 29.6748, 'longitude': -82.3577, 'FIPS_STATE_CODE': '12', 'county_fips_code': '12001'},
    {'county': 'Baker County', 'state': 'Florida', 'latitude': 30.3200, 'longitude': -82.2700, 'FIPS_STATE_CODE': '12', 'county_fips_code': '12003'},
    {'county': 'Bay County', 'state': 'Florida', 'latitude': 30.2572, 'longitude': -85.6027, 'FIPS_STATE_CODE': '12', 'county_fips_code': '12005'},
    {'county': 'Bradford County', 'state': 'Florida', 'latitude': 29.9500, 'longitude': -82.1700, 'FIPS_STATE_CODE': '12', 'county_fips_code': '12007'},
    {'county': 'Brevard County', 'state': 'Florida', 'latitude': 28.2639, 'longitude': -80.7214, 'FIPS_STATE_CODE': '12', 'county_fips_code': '12009'},
    # New York
    {'county': 'Albany County', 'state': 'New York', 'latitude': 42.6622, 'longitude': -73.8492, 'FIPS_STATE_CODE': '36', 'county_fips_code': '36001'},
    {'county': 'Allegany County', 'state': 'New York', 'latitude': 42.2574, 'longitude': -78.0276, 'FIPS_STATE_CODE': '36', 'county_fips_code': '36003'},
    {'county': 'Bronx County', 'state': 'New York', 'latitude': 40.8370, 'longitude': -73.8654, 'FIPS_STATE_CODE': '36', 'county_fips_code': '36005'},
    {'county': 'Broome County', 'state': 'New York', 'latitude': 42.1600, 'longitude': -75.8200, 'FIPS_STATE_CODE': '36', 'county_fips_code': '36007'},
    {'county': 'Cattaraugus County', 'state': 'New York', 'latitude': 42.2303, 'longitude': -78.6382, 'FIPS_STATE_CODE': '36', 'county_fips_code': '36009'},
    # Illinois
    {'county': 'Adams County', 'state': 'Illinois', 'latitude': 39.9948, 'longitude': -91.1705, 'FIPS_STATE_CODE': '17', 'county_fips_code': '17001'},
    {'county': 'Alexander County', 'state': 'Illinois', 'latitude': 37.1916, 'longitude': -89.3376, 'FIPS_STATE_CODE': '17', 'county_fips_code': '17003'},
    {'county': 'Bond County', 'state': 'Illinois', 'latitude': 38.8970, 'longitude': -89.4376, 'FIPS_STATE_CODE': '17', 'county_fips_code': '17005'},
    {'county': 'Boone County', 'state': 'Illinois', 'latitude': 42.3320, 'longitude': -88.8466, 'FIPS_STATE_CODE': '17', 'county_fips_code': '17007'},
    {'county': 'Brown County', 'state': 'Illinois', 'latitude': 40.0052, 'longitude': -90.7215, 'FIPS_STATE_CODE': '17', 'county_fips_code': '17009'},
]

num_patients = 5000
patients = []

medical_histories = ['Hypertension', 'Diabetes', 'Asthma', 'Arthritis', 'None', 'High Cholesterol', 'Depression']
pharmacies = ['CVS', 'Walgreens', 'Rite Aid', 'Walmart Pharmacy', 'Costco Pharmacy', 'Independent Pharmacy']
genders = ['Male', 'Female']
marital_statuses = ['Single', 'Married', 'Divorced', 'Widowed']
drug_needs = ['Painkillers', 'Antidepressants', 'Blood Pressure Medication', 'Statins', 'Insulin', 'None']
ethnicities = ['White', 'Hispanic', 'Black', 'Asian', 'American Indian or Alaska Native', 'Native Hawaiian or Other Pacific Islander', 'Two or More Races']
ethnicity_weights = [0.58, 0.20, 0.13, 0.06, 0.01, 0.005, 0.015] # Approximate US distribution

# Generate synthetic NPI numbers for each pharmacy
pharmacy_npi = {name: str(random.randint(1000000000, 9999999999)) for name in pharmacies}

for i in range(num_patients):
    age = random.randint(18, 95)
    gender = random.choice(genders)
    
    is_pregnant = False
    if gender == 'Female' and 18 <= age <= 45:
        is_pregnant = random.choice([True, False])

    county_info = random.choice(county_data)
    pharmacy_name = random.choice(pharmacies)

    patient = {
        'patient_id': i + 1,
        'age': age,
        'gender': gender,
        'marital_status': random.choice(marital_statuses),
        'number_of_children': random.randint(0, 5) if age > 20 else 0,
        'annual_salary': round(np.random.lognormal(mean=11, sigma=0.7)),
        'us_county': county_info['county'],
        'us_state': county_info['state'],
        'latitude': county_info['latitude'],
        'longitude': county_info['longitude'],
        'FIPS_STATE_CODE': county_info['FIPS_STATE_CODE'],
        'county_fips_code': county_info['county_fips_code'],
        'medical_history': random.sample(medical_histories, k=random.randint(1, 3)),
        'nearest_pharmacy': pharmacy_name,
        'NPI_NBR': pharmacy_npi[pharmacy_name],
        'distance_to_pharmacy_km': round(random.uniform(0.5, 25.0), 2),
        'is_senior_citizen': age >= 65,
        'is_pregnant': is_pregnant,
        'has_college_degree': random.choice([True, False]),
        'ethnicity': random.choices(ethnicities, weights=ethnicity_weights, k=1)[0],
        'drug_needs': random.choice(drug_needs),
        'has_chronic_illness': random.choices([True, False], weights=[0.3, 0.7], k=1)[0],
        'last_checkup_date': (datetime.now() - timedelta(days=random.randint(30, 1095))).strftime('%Y-%m-%d'),
        'blood_pressure': f"{random.randint(110, 160)}/{random.randint(70, 100)}",
        'heart_rate': random.randint(60, 100)
    }
    patients.append(patient)

df = pd.DataFrame(patients)

# Add total number of patients per county
df['patients_in_county'] = df.groupby('us_county')['us_county'].transform('count')

output_path = r"C:\Users\703401801\Desktop\synthetic_patient_data.csv"
df.to_csv(output_path, index=False)

print(f"Successfully generated {num_patients} patient records and saved to {output_path}")

```

## 2. Cluster Analysis and Excel Report Script

**Prompt:** *"Please tabulate these cluster findings and store them in the following location - "C:\Users\703401801\Desktop". Please store them as an excel file."*

This script performs a geographic clustering of patients and saves a detailed report, with a separate sheet for each cluster, to an Excel file.

```python
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def tabulate_cluster_analysis():
    # Define output path
    output_path = r"C:\Users\703401801\Desktop\cluster_analysis_results.xlsx"

    # Load the dataset
    try:
        df = pd.read_csv(r"C:\Users\703401801\Desktop\Cigna\synthetic_patient_data.csv")
    except FileNotFoundError:
        print("Error: The file 'synthetic_patient_data.csv' was not found.")
        return

    # --- 1. Geographic Clustering ---
    coords = df[['latitude', 'longitude']]
    scaler = StandardScaler()
    coords_scaled = scaler.fit_transform(coords)
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(coords_scaled)

    # --- 2. Region Mapping ---
    centroids = scaler.inverse_transform(kmeans.cluster_centers_)
    lat_sorted_indices = sorted(range(len(centroids)), key=lambda k: centroids[k][0])
    lon_sorted_indices = sorted(range(len(centroids)), key=lambda k: centroids[k][1])

    cluster_map = {}
    cluster_map[lon_sorted_indices[0]] = "West"
    cluster_map[lon_sorted_indices[-1]] = "East"
    cluster_map[lat_sorted_indices[-1]] = "North"
    cluster_map[lat_sorted_indices[0]] = "South"
    
    for i in range(5):
        if i not in cluster_map:
            cluster_map[i] = "Central"
            break

    df['region'] = df['cluster'].map(cluster_map)

    # --- 3. Create Excel Report ---
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for region_name in ["North", "West", "South", "East", "Central"]:
            cluster_df = df[df['region'] == region_name]
            if cluster_df.empty:
                continue

            # --- Create Summary DataFrames ---
            
            # General Characteristics
            general_stats = pd.DataFrame({
                'Metric': ['Total Patients', 'Average Age (years)', 'Average Annual Salary', 'Average Number of Children'],
                'Value': [
                    len(cluster_df),
                    f"{cluster_df['age'].mean():.1f}",
                    f"${cluster_df['annual_salary'].mean():,.2f}",
                    f"{cluster_df['number_of_children'].mean():.2f}"
                ]
            }).set_index('Metric')

            # Demographics
            demographics = pd.DataFrame({
                'Metric': ['Most Common Marital Status', 'College Degree Holders (%)'],
                'Value': [
                    cluster_df['marital_status'].mode()[0],
                    f"{cluster_df['has_college_degree'].mean()*100:.1f}%"
                ]
            }).set_index('Metric')
            gender_dist = cluster_df['gender'].value_counts(normalize=True).mul(100).round(1).rename('Gender Distribution (%)')
            ethnicity_dist = cluster_df['ethnicity'].value_counts(normalize=True).mul(100).round(1).rename('Ethnicity Distribution (%)')

            # Health Profile
            try:
                exploded_history = cluster_df.copy()
                exploded_history['medical_history'] = exploded_history['medical_history'].apply(eval)
                exploded_history = exploded_history.explode('medical_history')
                common_conditions = exploded_history['medical_history'].value_counts().nlargest(3)
            except Exception:
                common_conditions = pd.Series({"Error": "Could not parse conditions"})

            health_profile = pd.DataFrame({
                'Metric': ['Most Common Drug Needs'],
                'Value': [cluster_df['drug_needs'].mode()[0]]
            }).set_index('Metric')
            common_conditions.name = 'Most Common Medical Conditions'

            # Pharmacy Distance
            county_distances = cluster_df.groupby('us_county')['distance_to_pharmacy_km'].mean().round(2).rename('Avg Distance (km)')

            # --- Write DataFrames to Excel Sheet ---
            start_row = 1
            general_stats.to_excel(writer, sheet_name=region_name, startrow=start_row, startcol=0)
            start_row += len(general_stats) + 2

            demographics.to_excel(writer, sheet_name=region_name, startrow=start_row, startcol=0)
            start_row += len(demographics) + 1
            gender_dist.to_excel(writer, sheet_name=region_name, startrow=start_row, startcol=0, header=True)
            start_row += len(gender_dist) + 2
            ethnicity_dist.to_excel(writer, sheet_name=region_name, startrow=start_row, startcol=0, header=True)
            start_row += len(ethnicity_dist) + 2

            health_profile.to_excel(writer, sheet_name=region_name, startrow=start_row, startcol=0)
            start_row += len(health_profile) + 1
            common_conditions.to_excel(writer, sheet_name=region_name, startrow=start_row, startcol=0, header=True)
            start_row += len(common_conditions) + 2

            county_distances.to_excel(writer, sheet_name=region_name, startrow=start_row, startcol=0, header=True)

            # Add a title
            worksheet = writer.sheets[region_name]
            worksheet.cell(row=1, column=1, value=f"{region_name.upper()} CLUSTER ANALYSIS")

    print(f"Successfully created cluster analysis report at {output_path}")

if __name__ == "__main__":
    tabulate_cluster_analysis()
```

## 3. Script to Add/Fix Cluster Column in CSV

**Prompt:** *"Based on the above result, can you add a cluster column in the file... Some of the patients dont have cluster allocations in the above file. Please update these."*

This script adds a `cluster` column to the main CSV file. This is the final, corrected version that ensures every patient is assigned a cluster.

```python
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os

def fix_cluster_column():
    # Define the file path
    file_path = r"C:\Users\703401801\Desktop\Cigna\synthetic_patient_data.csv"

    # Load the dataset
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return

    # Drop the old, faulty cluster column if it exists
    if 'cluster' in df.columns:
        df = df.drop(columns=['cluster'])

    # --- 1. Geographic Clustering ---
    if not pd.api.types.is_numeric_dtype(df['latitude']) or not pd.api.types.is_numeric_dtype(df['longitude']):
        print("Error: Latitude and Longitude columns must be numeric for clustering.")
        return
        
    coords = df[['latitude', 'longitude']]
    scaler = StandardScaler()
    coords_scaled = scaler.fit_transform(coords)
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    df['cluster_id'] = kmeans.fit_predict(coords_scaled)

    # --- 2. Corrected Region Mapping ---
    centroids = scaler.inverse_transform(kmeans.cluster_centers_)
    lat_sorted_indices = sorted(range(len(centroids)), key=lambda k: centroids[k][0])
    lon_sorted_indices = sorted(range(len(centroids)), key=lambda k: centroids[k][1])

    cluster_map = {}
    available_regions = ["North", "South", "East", "West", "Central"]

    # Assign North and South, as they are the most distinct vertically
    north_idx = lat_sorted_indices[-1]
    cluster_map[north_idx] = "North"
    available_regions.remove("North")

    south_idx = lat_sorted_indices[0]
    cluster_map[south_idx] = "South"
    available_regions.remove("South")

    # Assign East and West if they haven't been taken by North/South
    east_idx = lon_sorted_indices[-1]
    if east_idx not in cluster_map:
        cluster_map[east_idx] = "East"
        available_regions.remove("East")

    west_idx = lon_sorted_indices[0]
    if west_idx not in cluster_map:
        cluster_map[west_idx] = "West"
        available_regions.remove("West")

    # Assign any remaining regions to the unmapped clusters
    for i in range(5):
        if i not in cluster_map:
            cluster_map[i] = available_regions.pop(0)

    df['cluster'] = df['cluster_id'].map(cluster_map)
    df = df.drop(columns=['cluster_id'])

    # --- 3. Verification and Save ---
    missing_after_fix = df['cluster'].isnull().sum()
    if missing_after_fix > 0:
        print(f"Error: Could not fix the cluster allocation. {missing_after_fix} rows are still null.")
    else:
        try:
            df.to_csv(file_path, index=False)
            print(f"Successfully fixed and updated the 'cluster' column in {file_path}")
        except PermissionError:
            print(f"Error: Permission denied. Could not write to {file_path}. Please ensure the file is not open.")

if __name__ == "__main__":
    fix_cluster_column()
```

## 4. Pharmacy Location Optimization Script

**Prompt:** *"Please now undertake an analysis to identify the optimal pharmacy location for each patient such that the distance the patient needs to travel is less than 17 Kms... Why is the new distance from proposed pharmacy column 0 for most patients? Please update..."*

This script identifies the optimal locations for new pharmacies to serve patients who are currently more than 17km away. This is the final version which adds a "jitter" to patient coordinates for a more realistic distance calculation.

```python
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np
import random

def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great-circle distance between two points 
    on the earth (specified in decimal degrees).
    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371 # Radius of earth in kilometers.
    return c * r

def find_optimal_pharmacies_with_jitter():Yes
    file_path = r"C:\Users\703401801\Desktop\Cigna\synthetic_patient_data.csv"

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return

    # Drop old proposed columns if they exist
    cols_to_drop = ['proposed_pharmacy_longitude_latitude', 'proposed_pharmacy_location_us_county', 'new_distance_to_nearest_proposed_pharmacy']
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')

    target_patients = df[df['distance_to_pharmacy_km'] > 17].copy()

    if target_patients.empty:
        print("No patients found with distance to pharmacy > 17 km. No changes needed.")
        return

    coords = target_patients[['latitude', 'longitude']].values

    k = 1
    while True:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        target_patients['new_cluster'] = kmeans.fit_predict(coords)
        centroids = kmeans.cluster_centers_
        max_dist = 0
        for i in range(k):
            cluster_points = target_patients[target_patients['new_cluster'] == i][['latitude', 'longitude']].values
            centroid_loc = centroids[i]
            if len(cluster_points) > 0:
                distances = haversine_distance(cluster_points[:, 1], cluster_points[:, 0], centroid_loc[1], centroid_loc[0])
                max_dist = max(max_dist, np.max(distances))
        if max_dist <= 17:
            break
        k += 1
        if k > 100: # Increased safety break
            print("Could not find a solution with fewer than 100 new pharmacies. Aborting.")
            return

    all_counties = df[['us_county', 'latitude', 'longitude']].drop_duplicates().values
    proposed_pharmacies = []
    for i, centroid in enumerate(centroids):
        min_dist = float('inf')
        best_county = None
        for county_info in all_counties:
            dist = haversine_distance(centroid[1], centroid[0], county_info[2], county_info[1])
            if dist < min_dist:
                min_dist = dist
                best_county = county_info[0]
        proposed_pharmacies.append({
            'cluster_id': i,
            'pro_latitude': centroid[0],
            'pro_longitude': centroid[1],
            'pro_county': best_county
        })

    new_pharmacy_locations = pd.DataFrame(proposed_pharmacies)
    
    def find_nearest_pharmacy_with_jitter(lat, lon):
        # ADDING JITTER HERE FOR REALISTIC DISTANCES
        lat_jitter = lat + random.uniform(-0.05, 0.05) # Approx +/- 5.5 km
        lon_jitter = lon + random.uniform(-0.05, 0.05)

        distances = haversine_distance(lon_jitter, lat_jitter, new_pharmacy_locations['pro_longitude'], new_pharmacy_locations['pro_latitude'])
        nearest_idx = np.argmin(distances)
        nearest_pharmacy_info = new_pharmacy_locations.iloc[nearest_idx]
        return (
            f"{nearest_pharmacy_info['pro_latitude']:.4f}, {nearest_pharmacy_info['pro_longitude']:.4f}",
            nearest_pharmacy_info['pro_county'],
            distances[nearest_idx]
        )

    results = df.apply(lambda row: find_nearest_pharmacy_with_jitter(row['latitude'], row['longitude']), axis=1, result_type='expand')
    df[['proposed_pharmacy_longitude_latitude', 'proposed_pharmacy_location_us_county', 'new_distance_to_nearest_proposed_pharmacy']] = results

    try:
        df.to_csv(file_path, index=False)
        print(f"Successfully updated {file_path} with realistic, non-zero distances.")
    except PermissionError:
        print(f"Error: Permission denied when writing to {file_path}. Please ensure it is not open.")

if __name__ == "__main__":
    find_optimal_pharmacies_with_jitter()
```

## 5. Debugging Script for Checking Clusters

**Prompt:** *"Some of the patients dont have cluster allocations in the above file. Please update these."*

This was a one-off script used to diagnose the problem of missing cluster allocations.

```python
import pandas as pd

file_path = r"C:\Users\703401801\Desktop\Cigna\synthetic_patient_data.csv"

try:
    df = pd.read_csv(file_path)
    
    # Check if 'cluster' column exists
    if 'cluster' in df.columns:
        missing_clusters = df['cluster'].isnull().sum()
        if missing_clusters > 0:
            print(f"Found {missing_clusters} patients with no cluster allocation.")
            # Displaying a few rows where the cluster is missing
            print("Here are some of the rows with missing data:")
            print(df[df['cluster'].isnull()].head())
        else:
            print("No patients with missing cluster allocations were found. All rows seem to be populated.")
    else:
        print("The 'cluster' column does not exist in the file.")

except FileNotFoundError:
    print(f"Error: The file at {file_path} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
```
