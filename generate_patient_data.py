
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
