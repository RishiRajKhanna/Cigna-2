
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def tabulate_cluster_analysis():
    # Define output path
    output_path = r"C:\Users\703401801\Desktop\cluster_analysis_results.xlsx"

    # Load the dataset
    try:
        df = pd.read_csv("synthetic_patient_data_with_distances.csv")
    except FileNotFoundError:
        print("Error: The file 'synthetic_patient_data_with_distances.csv' was not found.")
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
