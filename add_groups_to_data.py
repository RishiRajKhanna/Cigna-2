import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os

def add_cluster_column():
    # Define the file path
    file_path = "synthetic_patient_data_with_distances.csv"

    # Load the dataset
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} rows from {file_path}")
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return

    # Drop the old cluster column if it exists
    if 'group' in df.columns:
        df = df.drop(columns=['group'])
        print("Dropped existing 'group' column")

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

    df['group'] = df['cluster_id'].map(cluster_map)
    df = df.drop(columns=['cluster_id'])

    # --- 3. Verification and Save ---
    missing_after_fix = df['group'].isnull().sum()
    if missing_after_fix > 0:
        print(f"Error: Could not add the group column. {missing_after_fix} rows are still null.")
    else:
        try:
            df.to_csv(file_path, index=False)
            print(f"Successfully added 'group' column to {file_path}")
            print(f"Group distribution:")
            print(df['group'].value_counts())
        except PermissionError:
            print(f"Error: Permission denied. Could not write to {file_path}. Please ensure the file is not open.")

if __name__ == "__main__":
    add_cluster_column()
