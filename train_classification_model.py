import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
import joblib

# Load the dataset
file_path = 'C:\\Users\\703401801\\Desktop\\Cigna\\synthetic_patient_data_with_clusters.csv'
df = pd.read_csv(file_path)

# Define features (X) and target (y)
X = df.drop('Pharmacy_Found_Class', axis=1)
y = df['Pharmacy_Found_Class']

# Define categorical and numerical features
categorical_features = ['medical_history', 'drug_needs', 'has_chronic_illness', 'is_senior_citizen', 'Group', 'us_county', 'us_state', 'gender', 'marital_status', 'ethnicity', 'last_checkup_date', 'blood_pressure']
numerical_features = ['age', 'annual_salary', 'number_of_children', 'latitude', 'longitude', 'FIPS_STATE_CODE', 'county_fips_code', 'heart_rate', 'patients_in_county', 'distance_to_nearest_pharmacy_miles']

# Create a preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# Create the model pipeline
model_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                 ('classifier', RandomForestClassifier(random_state=42))])

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model_pipeline.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model_pipeline.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f'Model Accuracy: {accuracy:.4f}')

# Save the trained model
model_path = 'C:\\Users\\703401801\\Desktop\\Cigna\\pharmacy_found_model.joblib'
joblib.dump(model_pipeline, model_path)
print(f'Model saved to: {model_path}')
