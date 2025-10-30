from flask import Flask, render_template, jsonify, request, url_for
from flask_cors import CORS
import pandas as pd
import numpy as np
import csv
from collections import defaultdict
import os
import joblib
from io import StringIO

app = Flask(__name__, template_folder='templates', static_folder='static')
# Allow cross-origin requests in case the frontend is served from a different origin/port
CORS(app)

# --- Fictitious Pharmacy Data (for demonstration) ---
PHARMACIES_DATA = [
    {"name": "MediCare Pharmacy", "latitude": 34.0522, "longitude": -118.2437, "specialties": ["General", "Diabetes"]},
    {"name": "HealthHub Rx", "latitude": 34.0550, "longitude": -118.2500, "specialties": ["General", "Hypertension"]},
    {"name": "QuickPill Pharmacy", "latitude": 34.0480, "longitude": -118.2350, "specialties": ["General", "Asthma"]},
    {"name": "Wellness Drugstore", "latitude": 34.0600, "longitude": -118.2600, "specialties": ["General", "Pain Management"]},
    {"name": "City Central Pharmacy", "latitude": 34.0500, "longitude": -118.2400, "specialties": ["General"]},
    {"name": "Rural Health Pharmacy", "latitude": 38.5545, "longitude": -89.1732, "specialties": ["General"]},
    {"name": "Mountain View Meds", "latitude": 39.4371, "longitude": -97.3851, "specialties": ["General"]},
]
pharmacies_df = pd.DataFrame(PHARMACIES_DATA)

# --- Haversine Distance Calculation ---
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in kilometers
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance_km = R * c
    return distance_km * 0.621371  # Convert to miles

# --- Function to load and process county data ---
def load_county_data(file_path):
    county_coords = defaultdict(lambda: {'latitudes': [], 'longitudes': []})
    unique_counties = []
    seen = set()

    try:
        with open(file_path, 'r', newline='') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    county_name = str(row['us_county']).strip()
                    state_name = str(row['us_state']).strip()
                    full_county_name = f"{county_name}, {state_name}"
                    norm_key = f"{county_name.lower()}, {state_name.lower()}"
                    
                    latitude = float(row.get('latitude', 0))
                    longitude = float(row.get('longitude', 0))

                    county_coords[full_county_name]['latitudes'].append(latitude)
                    county_coords[full_county_name]['longitudes'].append(longitude)
                    if norm_key not in seen:
                        seen.add(norm_key)
                        unique_counties.append(full_county_name)
                except (ValueError, KeyError):
                    continue
    except FileNotFoundError:
        return {}, []

    # Calculate average lat/lon for each county
    avg_county_coords = {}
    for county, coords in county_coords.items():
        if coords['latitudes'] and coords['longitudes']:
            avg_county_coords[county] = {
                'latitude': np.mean(coords['latitudes']),
                'longitude': np.mean(coords['longitudes'])
            }
        else:
            avg_county_coords[county] = {'latitude': 0, 'longitude': 0}

    # Sort case-insensitively
    unique_counties_sorted = sorted(unique_counties, key=lambda x: x.lower())
    return avg_county_coords, unique_counties_sorted

# Load county data at app startup (use paths relative to this file)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
county_data_file = os.path.join(BASE_DIR, 'synthetic_patient_data_with_distances.csv')
avg_county_coords, unique_county_names = load_county_data(county_data_file)

# If the primary file isn't found or results are empty, try a secondary known filename
if not unique_county_names:
    alt_county_file = os.path.join(BASE_DIR, 'synthetic_patient_data_with_distances_New.csv')
    avg_county_coords, unique_county_names = load_county_data(alt_county_file)

# Load the full patient data for analysis
try:
    patient_data_df = pd.read_csv(county_data_file)
    print(f"✓ Loaded patient data: {len(patient_data_df)} rows")
    print(f"  Columns: {list(patient_data_df.columns)}")
except FileNotFoundError:
    print(f"✗ Patient data file not found: {county_data_file}")
    patient_data_df = pd.DataFrame()
except Exception as e:
    print(f"✗ Error loading patient data: {e}")
    patient_data_df = pd.DataFrame()

# Load the trained ML model
try:
    model_path = os.path.join(BASE_DIR, 'pharmacy_found_model.joblib')
    ml_model = joblib.load(model_path)
    print(f"✓ Loaded ML model from {model_path}")
except FileNotFoundError:
    print(f"✗ ML model not found: {model_path}")
    ml_model = None
except Exception as e:
    print(f"✗ Error loading ML model: {e}")
    ml_model = None

# Load top counties data (relative path)
top_counties_path = os.path.join(BASE_DIR, 'total_patients_by_county.csv')
try:
    top_counties_df = pd.read_csv(top_counties_path)
    # Normalize whitespace for county names and drop duplicates
    top_counties_df['county'] = top_counties_df['county'].astype(str).str.strip()
    top_counties_df = top_counties_df.drop_duplicates(subset=['county'])
    top_13_counties = top_counties_df.head(13).copy()
    # Create a reproducible but random-looking fictitious desert population
    rng = np.random.default_rng(42)
    top_13_counties['fictitious_desert_population'] = (
        top_13_counties['total_patients'] * rng.uniform(0.1, 0.3, len(top_13_counties))
    )
except FileNotFoundError:
    top_13_counties = pd.DataFrame(columns=['county', 'total_patients', 'fictitious_desert_population'])

# Load pharmacy location suggestions
try:
    pharmacy_suggestions_path = os.path.join(BASE_DIR, 'pharmacy_location_suggestions.csv')
    pharmacy_suggestions_df = pd.read_csv(pharmacy_suggestions_path)
    print(f"✓ Loaded pharmacy suggestions: {len(pharmacy_suggestions_df)} rows")
except FileNotFoundError:
    print(f"✗ Pharmacy suggestions file not found, will generate from patient data")
    pharmacy_suggestions_df = pd.DataFrame()
except Exception as e:
    print(f"✗ Error loading pharmacy suggestions: {e}")
    pharmacy_suggestions_df = pd.DataFrame()

print(f"\n=== Data Loading Summary ===")
print(f"Patient data rows: {len(patient_data_df)}")
print(f"Unique counties: {len(unique_county_names)}")
print(f"ML model loaded: {ml_model is not None}")
print(f"Pharmacy suggestions: {len(pharmacy_suggestions_df)}")
print(f"===========================\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/debug')
def debug_info():
    """Debug endpoint to check data loading"""
    return jsonify({
        'patient_data_loaded': not patient_data_df.empty,
        'patient_data_rows': len(patient_data_df),
        'patient_data_columns': list(patient_data_df.columns) if not patient_data_df.empty else [],
        'ml_model_loaded': ml_model is not None,
        'pharmacy_suggestions_loaded': not pharmacy_suggestions_df.empty,
        'pharmacy_suggestions_rows': len(pharmacy_suggestions_df),
        'unique_counties': len(unique_county_names),
        'sample_patient_data': patient_data_df.head(2).to_dict('records') if not patient_data_df.empty else []
    })

@app.route('/api/counties')
def get_counties():
    return jsonify({'counties': unique_county_names})

@app.route('/api/find_pharmacies', methods=['POST'])
def find_pharmacies():
    data = request.json
    selected_county = data.get('county')
    medical_conditions = data.get('medical_conditions', [])
    
    if not selected_county or selected_county not in avg_county_coords:
        return jsonify({'error': 'Invalid county selected'}), 400
    
    user_lat = avg_county_coords[selected_county]['latitude']
    user_lon = avg_county_coords[selected_county]['longitude']
    
    # Calculate distances
    distances = pharmacies_df.apply(
        lambda row: haversine_distance(user_lat, user_lon, row['latitude'], row['longitude']),
        axis=1
    )
    pharmacies_df['distance_miles'] = distances
    
    # Get nearest pharmacy
    nearest_pharmacy = pharmacies_df.sort_values(by='distance_miles').iloc[0]
    
    # Get relevant pharmacies based on medical conditions
    relevant_pharmacies = []
    if medical_conditions:
        relevant_df = pharmacies_df[
            pharmacies_df['specialties'].apply(lambda x: any(cond in x for cond in medical_conditions))
        ].sort_values(by='distance_miles')
        
        for idx, pharmacy in relevant_df.head(3).iterrows():
            relevant_pharmacies.append({
                'name': pharmacy['name'],
                'distance': round(pharmacy['distance_miles'], 2),
                'specialties': pharmacy['specialties'],
                'latitude': pharmacy['latitude'],
                'longitude': pharmacy['longitude']
            })
    
    # Get all nearby pharmacies
    all_nearby = []
    for idx, pharmacy in pharmacies_df.sort_values(by='distance_miles').head(5).iterrows():
        all_nearby.append({
            'name': pharmacy['name'],
            'distance': round(pharmacy['distance_miles'], 2),
            'specialties': pharmacy['specialties'],
            'latitude': pharmacy['latitude'],
            'longitude': pharmacy['longitude']
        })
    
    return jsonify({
        'nearest': {
            'name': nearest_pharmacy['name'],
            'distance': round(nearest_pharmacy['distance_miles'], 2),
            'latitude': nearest_pharmacy['latitude'],
            'longitude': nearest_pharmacy['longitude'],
            'specialties': nearest_pharmacy['specialties']
        },
        'relevant': relevant_pharmacies,
        'all_nearby': all_nearby,
        'user_coords': {'lat': user_lat, 'lon': user_lon}
    })

@app.route('/api/desert_counties')
def get_desert_counties():
    if top_13_counties.empty:
        return jsonify({'counties': [], 'total_desert_population': 0})
    
    counties_data = []
    for idx, row in top_13_counties.iterrows():
        counties_data.append({
            'county': row['county'],
            'total_patients': int(row['total_patients']),
            'desert_population': float(row['fictitious_desert_population'])
        })
    
    total_desert_pop = float(top_13_counties['fictitious_desert_population'].sum())
    
    return jsonify({
        'counties': counties_data,
        'total_desert_population': total_desert_pop
    })

# --- TAB 2: Cluster Analysis API ---
@app.route('/api/clusters')
def get_clusters():
    """Get unique cluster/group names from the data"""
    if patient_data_df.empty or 'group' not in patient_data_df.columns:
        return jsonify({'clusters': []})
    
    clusters = sorted(patient_data_df['group'].dropna().unique().tolist())
    return jsonify({'clusters': clusters})

@app.route('/api/cluster_analysis', methods=['POST'])
def analyze_cluster():
    """Analyze a specific cluster by subgroups"""
    data = request.json
    selected_cluster = data.get('cluster')
    
    if patient_data_df.empty or not selected_cluster:
        return jsonify({'error': 'Invalid cluster or no data available'}), 400
    
    cluster_data = patient_data_df[patient_data_df['group'] == selected_cluster].copy()
    
    if cluster_data.empty:
        return jsonify({'error': 'No data for selected cluster'}), 404
    
    analysis = {
        'cluster': selected_cluster,
        'total_patients': int(len(cluster_data)),
        'avg_distance': float(cluster_data['distance_to_nearest_pharmacy_miles'].mean()),
        'median_distance': float(cluster_data['distance_to_nearest_pharmacy_miles'].median()),
        'max_distance': float(cluster_data['distance_to_nearest_pharmacy_miles'].max()),
        'min_distance': float(cluster_data['distance_to_nearest_pharmacy_miles'].min()),
        'subgroups': {}
    }
    
    # Analyze by different subgroups
    subgroup_columns = ['gender', 'marital_status', 'ethnicity', 'is_senior_citizen', 
                        'is_pregnant', 'has_chronic_illness', 'has_college_degree']
    
    for col in subgroup_columns:
        if col in cluster_data.columns:
            subgroup_stats = cluster_data.groupby(col)['distance_to_nearest_pharmacy_miles'].agg([
                ('count', 'count'),
                ('avg_distance', 'mean'),
                ('median_distance', 'median')
            ]).reset_index()
            
            analysis['subgroups'][col] = [
                {
                    'value': str(row[col]),
                    'count': int(row['count']),
                    'avg_distance': round(float(row['avg_distance']), 2),
                    'median_distance': round(float(row['median_distance']), 2)
                }
                for _, row in subgroup_stats.iterrows()
            ]
    
    return jsonify(analysis)

# --- TAB 3: Pharmacy Desert & Suggestions API ---
@app.route('/api/pharmacy_deserts')
def get_pharmacy_deserts():
    """Get counties with distance > 10 miles (pharmacy deserts)"""
    if patient_data_df.empty:
        return jsonify({'desert_counties': [], 'total_affected': 0, 'avg_distance': 0})
    
    desert_data = patient_data_df[patient_data_df['distance_to_nearest_pharmacy_miles'] > 10].copy()
    
    if desert_data.empty:
        return jsonify({'desert_counties': [], 'total_affected': 0, 'avg_distance': 0})
    
    county_stats = desert_data.groupby(['us_county', 'us_state']).agg({
        'patient_id': 'count',
        'distance_to_nearest_pharmacy_miles': 'mean',
        'latitude': 'mean',
        'longitude': 'mean'
    }).reset_index()
    
    county_stats.columns = ['county', 'state', 'affected_patients', 'avg_distance', 'latitude', 'longitude']
    county_stats = county_stats.sort_values('affected_patients', ascending=False)
    
    desert_counties = []
    for _, row in county_stats.iterrows():
        desert_counties.append({
            'county': f"{row['county']}, {row['state']}",
            'affected_patients': int(row['affected_patients']),
            'avg_distance': round(float(row['avg_distance']), 2),
            'latitude': float(row['latitude']),
            'longitude': float(row['longitude'])
        })
    
    # Calculate overall average distance for desert areas
    overall_avg_distance = float(desert_data['distance_to_nearest_pharmacy_miles'].mean())
    
    return jsonify({
        'desert_counties': desert_counties,
        'total_affected': int(len(desert_data)),
        'avg_distance': round(overall_avg_distance, 2)
    })

@app.route('/api/pharmacy_suggestions')
def get_pharmacy_suggestions():
    """Get suggested pharmacy locations from pre-computed suggestions"""
    if not pharmacy_suggestions_df.empty:
        # Use pre-computed suggestions from CSV
        suggestions = []
        for _, row in pharmacy_suggestions_df.iterrows():
            # Map the CSV columns to expected format
            potential_patients = int(row.get('desert_population', row.get('potential_patients', 0)))
            # Prefer county geo-centroids over CSV lat/lon
            county_label = str(row.get('county', 'Unknown'))
            if county_label in avg_county_coords:
                lat = float(avg_county_coords[county_label]['latitude'])
                lon = float(avg_county_coords[county_label]['longitude'])
            else:
                lat = float(row.get('suggested_latitude', row.get('latitude', 0)))
                lon = float(row.get('suggested_longitude', row.get('longitude', 0)))
            
            # Calculate cost based on patient volume
            base_cost = 500000
            patient_multiplier = potential_patients * 1000
            estimated_cost = base_cost + patient_multiplier
            
            suggestions.append({
                'county': str(row.get('county', 'Unknown')),
                'latitude': lat,
                'longitude': lon,
                'potential_patients': potential_patients,
                'estimated_cost': estimated_cost
            })
        
        return jsonify({'suggestions': suggestions})
    
    # Generate basic suggestions from desert areas if file not available
    if patient_data_df.empty:
        return jsonify({'suggestions': []})
    
    desert_data = patient_data_df[patient_data_df['distance_to_nearest_pharmacy_miles'] > 10].copy()
    county_centers = desert_data.groupby(['us_county', 'us_state']).agg({
        'latitude': 'mean',
        'longitude': 'mean',
        'patient_id': 'count'
    }).reset_index()
    
    county_centers = county_centers.sort_values('patient_id', ascending=False).head(15)
    
    suggestions = []
    for idx, row in county_centers.iterrows():
        # Estimate property cost (simplified)
        base_cost = 500000
        patient_multiplier = row['patient_id'] * 1000
        estimated_cost = base_cost + patient_multiplier
        
        county_label = f"{row['us_county']}, {row['us_state']}"
        # Use centroid if available, else fallback to grouped mean
        centroid = avg_county_coords.get(county_label)
        cent_lat = float(centroid['latitude']) if centroid else float(row['latitude'])
        cent_lon = float(centroid['longitude']) if centroid else float(row['longitude'])

        suggestions.append({
            'county': county_label,
            'latitude': cent_lat,
            'longitude': cent_lon,
            'potential_patients': int(row['patient_id']),
            'estimated_cost': int(estimated_cost)
        })
    
    return jsonify({'suggestions': suggestions})

# --- TAB 4: File Upload & ML Prediction API ---
@app.route('/api/predict_pharmacy', methods=['POST'])
def predict_pharmacy():
    """
    Upload patient CSV file and predict pharmacy finding probability using Random Forest model.
    
    Expected CSV columns (at minimum):
    - patient_id: Unique identifier
    - age: Patient age
    - gender: Male/Female
    - marital_status: Single/Married/Divorced/Widowed
    - number_of_children: Integer
    - annual_salary: Float
    - is_senior_citizen: Boolean (True/False or 1/0)
    - is_pregnant: Boolean
    - has_chronic_illness: Boolean
    - has_college_degree: Boolean (optional)
    - ethnicity: White/Black/Hispanic/Asian (optional)
    - distance_to_nearest_pharmacy_miles: Float (optional, for comparison)
    
    Returns:
    - Descriptive statistics of uploaded patients
    - Top 10 patients with highest probability of finding pharmacy
    - Overall probability metrics
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are supported'}), 400
    
    try:
        # Read uploaded CSV
        content = file.read().decode('utf-8')
        uploaded_df = pd.read_csv(StringIO(content))
        
        print(f"\n=== File Upload Processing ===")
        print(f"Uploaded file: {file.filename}")
        print(f"Rows: {len(uploaded_df)}")
        print(f"Columns: {list(uploaded_df.columns)}")
        
        # Normalize patient_id column: accept common variants and preserve original values
        pid_candidates = ['patient_id', 'patient id', 'Patient ID', 'patientId', 'patientId', 'id', 'ID', 'pid']
        found_pid = None
        for col in uploaded_df.columns:
            if col in pid_candidates or col.lower().replace(' ', '') in ('patientid', 'id', 'pid'):
                found_pid = col
                break

        if found_pid and found_pid != 'patient_id':
            # Create a normalized column without altering original column names
            uploaded_df['patient_id'] = uploaded_df[found_pid]

        # Validate minimum required columns
        required_cols = ['patient_id', 'age', 'gender']
        missing_cols = [col for col in required_cols if col not in uploaded_df.columns]
        if missing_cols:
            return jsonify({'error': f'Missing required columns: {", ".join(missing_cols)}'}), 400
        
        # Calculate descriptive statistics
        stats = {
            'total_patients': int(len(uploaded_df)),
            'filename': file.filename,
            'upload_timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Age statistics
        if 'age' in uploaded_df.columns:
            stats['avg_age'] = round(float(uploaded_df['age'].mean()), 1)
            stats['min_age'] = int(uploaded_df['age'].min())
            stats['max_age'] = int(uploaded_df['age'].max())
            stats['median_age'] = int(uploaded_df['age'].median())
        
        # Gender distribution
        if 'gender' in uploaded_df.columns:
            gender_dist = uploaded_df['gender'].value_counts().to_dict()
            stats['gender_distribution'] = {str(k): int(v) for k, v in gender_dist.items()}
        
        # Marital status distribution
        if 'marital_status' in uploaded_df.columns:
            marital_dist = uploaded_df['marital_status'].value_counts().to_dict()
            stats['marital_status_distribution'] = {str(k): int(v) for k, v in marital_dist.items()}
        
        # Ethnicity distribution
        if 'ethnicity' in uploaded_df.columns:
            ethnicity_dist = uploaded_df['ethnicity'].value_counts().to_dict()
            stats['ethnicity_distribution'] = {str(k): int(v) for k, v in ethnicity_dist.items()}
        
        # Boolean flags
        stats['senior_count'] = int(uploaded_df['is_senior_citizen'].sum()) if 'is_senior_citizen' in uploaded_df.columns else 0
        stats['pregnant_count'] = int(uploaded_df['is_pregnant'].sum()) if 'is_pregnant' in uploaded_df.columns else 0
        stats['chronic_illness_count'] = int(uploaded_df['has_chronic_illness'].sum()) if 'has_chronic_illness' in uploaded_df.columns else 0
        stats['college_degree_count'] = int(uploaded_df['has_college_degree'].sum()) if 'has_college_degree' in uploaded_df.columns else 0
        
        # Salary statistics
        if 'annual_salary' in uploaded_df.columns:
            stats['avg_salary'] = round(float(uploaded_df['annual_salary'].mean()), 2)
            stats['median_salary'] = round(float(uploaded_df['annual_salary'].median()), 2)
        
        # Children statistics
        if 'number_of_children' in uploaded_df.columns:
            stats['avg_children'] = round(float(uploaded_df['number_of_children'].mean()), 2)
        
        # Existing distance statistics (if available)
        if 'distance_to_nearest_pharmacy_miles' in uploaded_df.columns:
            stats['avg_distance'] = round(float(uploaded_df['distance_to_nearest_pharmacy_miles'].mean()), 2)
            stats['median_distance'] = round(float(uploaded_df['distance_to_nearest_pharmacy_miles'].median()), 2)
        
        # ==================== ML MODEL PREDICTION ====================
        predictions = []
        
        if ml_model is None:
            stats['model_status'] = 'Model not loaded - predictions unavailable'
            print("⚠ ML model not available for predictions")
        else:
            try:
                print("\n=== Running ML Predictions ===")
                
                # Try to infer expected columns from the trained pipeline
                expected_num = []
                expected_cat = []
                try:
                    preprocessor = getattr(ml_model, 'named_steps', {}).get('preprocessor', None)
                    if preprocessor is not None:
                        # transformers_: [(name, transformer, columns), ...]
                        for name, _, cols in preprocessor.transformers_:
                            if name == 'num':
                                expected_num = list(cols)
                            elif name == 'cat':
                                expected_cat = list(cols)
                except Exception as _:
                    pass

                # Fallback to training-time defaults if not discoverable
                if not expected_num and not expected_cat:
                    expected_num = ['age', 'annual_salary', 'number_of_children', 'latitude', 'longitude',
                                    'FIPS_STATE_CODE', 'county_fips_code', 'heart_rate', 'patients_in_county',
                                    'distance_to_nearest_pharmacy_miles']
                    expected_cat = ['medical_history', 'drug_needs', 'has_chronic_illness', 'is_senior_citizen',
                                    'Group', 'us_county', 'us_state', 'gender', 'marital_status', 'ethnicity',
                                    'last_checkup_date', 'blood_pressure']

                # Handle naming mismatches (e.g., 'group' -> 'Group')
                if 'Group' in expected_cat and 'Group' not in uploaded_df.columns and 'group' in uploaded_df.columns:
                    uploaded_df['Group'] = uploaded_df['group']
                
                # Build feature frame with all expected columns
                feature_df = pd.DataFrame(index=uploaded_df.index)

                # Numeric: ensure existence and fill NaNs with 0
                for col in expected_num:
                    if col in uploaded_df.columns:
                        # Coerce to numeric when possible
                        feature_df[col] = pd.to_numeric(uploaded_df[col], errors='coerce').fillna(0)
                    else:
                        feature_df[col] = 0
                        print(f"⚠ Missing numeric column '{col}', defaulting to 0")

                # Categorical: pass-through as string; default to 'Unknown'
                for col in expected_cat:
                    if col in uploaded_df.columns:
                        feature_df[col] = uploaded_df[col].astype(str).fillna('Unknown')
                    else:
                        # Provide a reasonable default per column when helpful
                        default_value = 'Unknown'
                        if col in ['medical_history', 'drug_needs']:
                            default_value = 'None'
                        elif col in ['has_chronic_illness', 'is_senior_citizen']:
                            default_value = False
                        feature_df[col] = default_value
                        print(f"⚠ Missing categorical column '{col}', defaulting to {default_value}")

                # Keep only expected columns in the right order
                feature_df = feature_df[expected_num + expected_cat]

                print(f"Feature matrix shape: {feature_df.shape}")
                print(f"Numeric features: {expected_num}")
                print(f"Categorical features: {expected_cat}")
                
                # Make predictions
                if hasattr(ml_model, 'predict_proba'):
                    # Get probability of finding pharmacy (positive class)
                    probabilities = ml_model.predict_proba(feature_df)[:, 1]
                    print(f"✓ Predicted probabilities for {len(probabilities)} patients")
                else:
                    # Fallback to binary predictions
                    probabilities = ml_model.predict(feature_df).astype(float)
                    print(f"✓ Model returned binary predictions, converting to probabilities")
                
                # Add probabilities to dataframe
                uploaded_df['pharmacy_find_probability'] = probabilities
                
                # Calculate probability statistics
                stats['avg_probability'] = round(float(probabilities.mean()), 4)
                stats['median_probability'] = round(float(np.median(probabilities)), 4)
                stats['min_probability'] = round(float(probabilities.min()), 4)
                stats['max_probability'] = round(float(probabilities.max()), 4)
                stats['std_probability'] = round(float(probabilities.std()), 4)
                
                # Probability distribution buckets
                high_prob_count = int((probabilities >= 0.7).sum())
                medium_prob_count = int(((probabilities >= 0.4) & (probabilities < 0.7)).sum())
                low_prob_count = int((probabilities < 0.4).sum())
                
                stats['probability_distribution'] = {
                    'high (≥0.7)': high_prob_count,
                    'medium (0.4-0.7)': medium_prob_count,
                    'low (<0.4)': low_prob_count
                }
                
                # Keep original sequence – do NOT sort by probability.
                # If duplicate patient_ids exist, keep first occurrence to preserve order.
                if 'patient_id' in uploaded_df.columns:
                    unique_df = uploaded_df.drop_duplicates(subset=['patient_id'], keep='first').copy()
                    stats['deduplicated_by_patient_id'] = True
                    stats['unique_patient_count'] = int(len(unique_df))
                else:
                    unique_df = uploaded_df
                    stats['deduplicated_by_patient_id'] = False

                # Take the first 10 in original order
                top_patients = unique_df.head(10)
                
                for _, row in top_patients.iterrows():
                    # Preserve original patient_id format (strings, leading zeros, alphanumeric IDs)
                    raw_pid = row.get('patient_id', None)
                    # If the value is nan/None, use 'Unknown'
                    if pd.isna(raw_pid) or raw_pid is None:
                        pid_value = 'Unknown'
                    else:
                        pid_value = str(raw_pid)

                    pred_entry = {
                        'patient_id': pid_value,
                        'age': int(row.get('age', 0)),
                        'gender': str(row.get('gender', 'Unknown')),
                        'probability': round(float(row['pharmacy_find_probability']), 4),
                    }
                    
                    # Add optional fields if available
                    if 'marital_status' in row:
                        pred_entry['marital_status'] = str(row['marital_status'])
                    
                    if 'is_senior_citizen' in row:
                        pred_entry['is_senior_citizen'] = bool(row['is_senior_citizen'])
                    
                    if 'is_pregnant' in row:
                        pred_entry['is_pregnant'] = bool(row['is_pregnant'])
                    
                    if 'has_chronic_illness' in row:
                        pred_entry['has_chronic_illness'] = bool(row['has_chronic_illness'])
                    
                    if 'distance_to_nearest_pharmacy_miles' in row:
                        pred_entry['current_distance'] = round(float(row['distance_to_nearest_pharmacy_miles']), 2)
                    
                    if 'annual_salary' in row:
                        pred_entry['annual_salary'] = int(row['annual_salary'])
                    
                    predictions.append(pred_entry)
                
                # --- Build exportable CSV with only necessary fields ---
                export_cols = []
                for c in ['patient_id','age','gender','marital_status','is_senior_citizen','is_pregnant','has_chronic_illness','distance_to_nearest_pharmacy_miles','pharmacy_find_probability']:
                    if c in uploaded_df.columns or c == 'pharmacy_find_probability':
                        export_cols.append(c)

                export_df = uploaded_df[export_cols].copy()
                exports_dir = os.path.join(BASE_DIR, 'static', 'exports')
                os.makedirs(exports_dir, exist_ok=True)
                csv_name = f"predictions_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
                export_path = os.path.join(exports_dir, csv_name)
                # Round probability to 4 decimals for file
                if 'pharmacy_find_probability' in export_df.columns:
                    export_df['pharmacy_find_probability'] = export_df['pharmacy_find_probability'].round(4)
                export_df.to_csv(export_path, index=False)
                stats['download_url'] = url_for('static', filename=f'exports/{csv_name}')

                stats['model_status'] = 'Success - Predictions generated'
                print(f"✓ Generated top 10 predictions")
                print(f"  Avg probability: {stats['avg_probability']}")
                print(f"  High prob patients: {high_prob_count}")
                
            except Exception as e:
                stats['model_status'] = f'Prediction error: {str(e)}'
                stats['prediction_error'] = str(e)
                print(f"✗ Prediction error: {e}")
                import traceback
                traceback.print_exc()
        
        print("=== Processing Complete ===\n")
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'top_predictions': predictions,
            'model_available': ml_model is not None,
            'predictions_generated': len(predictions) > 0
        })
        
    except pd.errors.EmptyDataError:
        return jsonify({'error': 'The uploaded CSV file is empty'}), 400
    except pd.errors.ParserError as e:
        return jsonify({'error': f'CSV parsing error: {str(e)}'}), 400
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
