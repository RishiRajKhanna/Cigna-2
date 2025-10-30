
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

def find_optimal_pharmacies_with_jitter():
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
