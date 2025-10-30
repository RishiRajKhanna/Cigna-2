# Quick Start Guide - Pharmacy Access Analysis Platform

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
Open PowerShell in the project directory and run:
```powershell
pip install -r requirements.txt
```

### Step 2: Start the Application
```powershell
python pharmacy_app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 3: Open in Browser
Navigate to: **http://localhost:5000**

---

## 📋 What You'll See

### Tab 1: Patient Distance Finder
1. Select your county from dropdown
2. Check medical conditions (if any)
3. Select pregnancy status
4. Click "Find Nearest Pharmacies"
5. View results:
   - Nearest pharmacy with distance
   - Specialized pharmacies for your conditions
   - All nearby pharmacies

### Tab 2: Cluster Analysis
1. Select a cluster/group (North, South, East, West, Central)
2. Click "Analyze Cluster"
3. View comprehensive statistics
4. Click subgroup tabs to analyze by:
   - Gender
   - Marital Status
   - Ethnicity
   - Senior Citizen Status
   - And more...
5. See visual chart at bottom

### Tab 3: Pharmacy Deserts & Suggestions
1. View automatic statistics of pharmacy deserts
2. See interactive USA map
3. Review suggested pharmacy locations
4. **Click checkboxes** next to counties
5. Watch map update with green markers
6. See total cost calculation update automatically

### Tab 4: Prediction Upload
1. Click upload area or drag CSV file
2. Wait for processing
3. View patient statistics
4. See gender distribution chart
5. Review **Top 10 patients** with highest probability of finding pharmacy
6. Check average and median probabilities

---

## ✅ Testing the Application

### Test Tab 1
- Select any county (e.g., "Cascade, Montana")
- Check "Diabetes" and "Hypertension"
- Select "Not Pregnant"
- Click "Find Nearest Pharmacies"
- You should see pharmacy results with distances

### Test Tab 2
- Select "North" cluster
- Click "Analyze Cluster"
- You should see statistics and subgroup analysis
- Click different subgroup tabs

### Test Tab 3
- Automatically loads pharmacy desert data
- Click checkboxes next to suggested locations
- Green markers should appear on map
- Total cost should update

### Test Tab 4
- Use `synthetic_patient_data_with_distances.csv` as test file
- Drag onto upload area OR click to browse
- Should see statistics and top 10 predictions
- (Note: Requires `pharmacy_found_model.joblib` for predictions)

---

## 🔧 Troubleshooting

### Issue: "Cannot connect to server"
**Solution**: Make sure Flask is running (python pharmacy_app.py)

### Issue: "No counties showing in dropdown"
**Solution**: Verify `synthetic_patient_data_with_distances.csv` exists

### Issue: "Map not displaying"
**Solution**: Check internet connection (map tiles load from OpenStreetMap)

### Issue: "No predictions in Tab 4"
**Solution**: Ensure `pharmacy_found_model.joblib` file exists in project directory

### Issue: Port 5000 already in use
**Solution**: 
```powershell
# Find and kill process on port 5000
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process
```

---

## 📁 Required Files

Ensure these files exist:
- ✅ `pharmacy_app.py` - Main application
- ✅ `templates/index.html` - Frontend HTML
- ✅ `static/css/styles.css` - Styling
- ✅ `static/js/app.js` - JavaScript
- ✅ `synthetic_patient_data_with_distances.csv` - Patient data
- ⚠️ `pharmacy_found_model.joblib` - ML model (optional for Tab 4)
- ⚠️ `pharmacy_location_suggestions.csv` - Pre-computed suggestions (optional)
- ✅ `total_patients_by_county.csv` - County statistics

---

## 🎯 Sample CSV for Tab 4 Upload

Create a test file `test_upload.csv`:
```csv
patient_id,age,gender,is_senior_citizen,is_pregnant,has_chronic_illness,annual_salary,number_of_children
1001,45,Male,False,False,True,65000,2
1002,72,Female,True,False,True,45000,0
1003,28,Female,False,True,False,52000,1
```

---

## 💡 Tips

1. **Tab 1**: Works best with real county names from your data
2. **Tab 2**: Try different clusters to see varying distance patterns
3. **Tab 3**: Select multiple counties to see total cost estimation
4. **Tab 4**: Larger CSV files take longer to process

---

## 🌐 Browser Recommendations

Best experience with:
- Google Chrome (recommended)
- Mozilla Firefox
- Microsoft Edge

---

## 📊 Expected Behavior

### Tab 1
- Shows 1 nearest pharmacy
- Shows 0-3 specialized pharmacies (based on conditions)
- Shows top 5 nearby pharmacies

### Tab 2
- Statistics for entire cluster
- 7 subgroup categories to analyze
- Interactive chart visualization

### Tab 3
- Multiple county suggestions
- Interactive map with markers
- Real-time cost calculation

### Tab 4
- File upload with drag-and-drop
- Descriptive statistics
- Top 10 predictions ranked by probability
- Visual charts

---

## 🎉 You're Ready!

The application is now fully functional with all 4 tabs implemented as requested. Enjoy exploring the pharmacy access analysis platform!

For detailed documentation, see `IMPLEMENTATION_COMPLETE.md`
