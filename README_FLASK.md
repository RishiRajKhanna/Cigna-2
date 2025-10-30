# Pharmacy Access & Desert Analysis - Flask Application

A modern web application for finding nearby pharmacies and analyzing pharmacy desert coverage, built with Flask, HTML, CSS, and JavaScript.

## Features

### 1. Find Nearest Pharmacy
- Select your county from a dropdown
- Optionally select medical conditions
- Find the nearest pharmacy with distance calculations
- View pharmacies that match your medical history
- See all nearby pharmacies in a table

### 2. Pharmacy Desert Analysis
- View top 13 counties by patient population
- Select counties to see their impact on reducing pharmacy desert population
- Real-time coverage percentage calculation
- Visual representation with bar charts
- Interactive county selection

## Project Structure

```
Cigna (1)/
├── app.py                          # Flask application backend
├── templates/
│   └── index.html                  # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css              # Stylesheet
│   └── js/
│       └── app.js                 # JavaScript functionality
├── requirements.txt                # Python dependencies
└── README_FLASK.md                # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Steps

1. **Navigate to the project directory:**
   ```bash
   cd "E:\Cigna (1)"
   ```

2. **Activate your virtual environment:**
   ```bash
   # If venv already exists
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Update file paths in app.py (if needed):**
   Open `app.py` and update these paths to match your data location:
   ```python
   COUNTY_DATA_FILE = r"C:\Users\703401801\Desktop\Cigna\synthetic_patient_data_with_distances.csv"
   TOP_COUNTIES_FILE = r"C:\Users\703401801\Desktop\Cigna\total_patients_by_county.csv"
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Open your browser:**
   Navigate to `http://localhost:5000`

## Usage

### Find Nearest Pharmacy Tab
1. Select your county from the dropdown menu
2. (Optional) Check any medical conditions that apply to you
3. Click "Find Pharmacies"
4. View results:
   - Nearest pharmacy with distance
   - Pharmacies matching your medical conditions
   - Table of all nearby pharmacies

### Pharmacy Desert Insights Tab
1. View the list of top 13 counties by patient population
2. Click on counties to select/deselect them
3. Watch the coverage percentage update in real-time
4. View the visual representation of covered vs uncovered populations

## API Endpoints

- `GET /` - Main application page
- `GET /api/counties` - Get list of all counties
- `GET /api/conditions` - Get list of medical conditions
- `POST /api/find-pharmacies` - Find pharmacies near a county
- `GET /api/top-counties` - Get top 13 counties by population
- `POST /api/calculate-coverage` - Calculate desert coverage for selected counties

## Technologies Used

### Backend
- **Flask** - Python web framework
- **Pandas** - Data manipulation and analysis
- **NumPy** - Mathematical computations

### Frontend
- **HTML5** - Structure
- **CSS3** - Modern, responsive styling with CSS Grid and Flexbox
- **Vanilla JavaScript** - Interactive functionality, AJAX requests

## Features Highlights

### Modern UI Design
- Clean, professional interface
- Responsive design (mobile-friendly)
- Smooth animations and transitions
- Card-based layout
- Color-coded alerts and metrics

### Interactive Elements
- Tab-based navigation
- Dynamic form validation
- Real-time coverage calculations
- Clickable county cards
- Loading spinner for async operations

### Data Visualization
- Custom CSS-based bar charts
- Metric cards with gradients
- Responsive tables
- Color-coded alerts

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify the last line in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change port
```

### Data Files Not Found
Ensure the CSV files exist at the paths specified in `app.py`. Update the paths if your files are located elsewhere.

### Module Not Found
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Differences from Streamlit Version

- **Full control over UI/UX** with custom HTML/CSS
- **Better performance** with optimized JavaScript
- **More flexibility** for customization
- **Standard web stack** - easier to deploy
- **RESTful API** structure for potential mobile app integration

## Future Enhancements

- Map integration (Google Maps or Leaflet)
- User authentication
- Database integration
- Export functionality (PDF/CSV)
- Advanced filtering options
- Pharmacy reviews and ratings
- Real-time pharmacy availability

## License

This project is for demonstration purposes.
