// Global variables
let map;
let markers = [];
let selectedSuggestions = [];
let selectedIndices = new Set();
let clusterChart = null;
let genderChart = null;

// Tab 3 paging/filter state
let allSuggestions = [];
let filteredSuggestions = [];
let currentPage = 1;
const pageSize = 20;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    loadCounties();
    loadClusters();
    initializeTab3();
    initializeTab4();
});

// Tab Management
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');

            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            document.getElementById(tabId).classList.add('active');

            // Initialize map when tab3 is opened
            if (tabId === 'tab3') {
                setTimeout(() => {
                    initializeMap();
                    // Ensure map resizes after becoming visible
                    if (map) {
                        map.invalidateSize();
                    }
                }, 150);
            }
        });
    });
}

// ==================== TAB 1: Patient Distance Finder ====================

function loadCounties() {
    fetch('/api/counties')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('county-select');
            data.counties.forEach(county => {
                const option = document.createElement('option');
                option.value = county;
                option.textContent = county;
                select.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading counties:', error));
}

document.getElementById('find-pharmacy-btn').addEventListener('click', function() {
    const county = document.getElementById('county-select').value;
    const pregnancyStatus = document.getElementById('pregnancy-status').value === 'true';
    
    const medicalConditions = Array.from(document.querySelectorAll('input[name="medical"]:checked'))
        .map(checkbox => checkbox.value);

    if (!county) {
        alert('Please select a county');
        return;
    }

    fetch('/api/find_pharmacies', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            county: county,
            medical_conditions: medicalConditions,
            is_pregnant: pregnancyStatus
        })
    })
    .then(response => response.json())
    .then(data => {
        displayPharmacyResults(data, medicalConditions);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error finding pharmacies. Please try again.');
    });
});

function displayPharmacyResults(data, medicalConditions) {
    const resultsSection = document.getElementById('results-section');
    resultsSection.style.display = 'block';

    // Display nearest pharmacy
    const nearestDiv = document.getElementById('nearest-pharmacy');
    nearestDiv.innerHTML = `
        <p><strong>Name:</strong> ${data.nearest.name}</p>
        <p><strong>Distance:</strong> ${data.nearest.distance} miles</p>
        <p><strong>Specialties:</strong> ${data.nearest.specialties.join(', ')}</p>
    `;

    // Display specialized pharmacies
    const specializedSection = document.getElementById('specialized-pharmacies');
    const specializedList = document.getElementById('specialized-pharmacy-list');
    
    if (medicalConditions.length > 0 && data.relevant && data.relevant.length > 0) {
        specializedSection.style.display = 'block';
        specializedList.innerHTML = data.relevant.map(pharmacy => `
            <div style="margin-bottom: 15px; padding: 10px; background: #f3f4f6; border-radius: 8px;">
                <p><strong>Name:</strong> ${pharmacy.name}</p>
                <p><strong>Distance:</strong> ${pharmacy.distance} miles</p>
                <p><strong>Specialties:</strong> ${pharmacy.specialties.join(', ')}</p>
            </div>
        `).join('');
    } else {
        specializedSection.style.display = 'none';
    }

    // Display all nearby pharmacies
    const allPharmaciesDiv = document.getElementById('all-pharmacies');
    allPharmaciesDiv.innerHTML = data.all_nearby.map(pharmacy => `
        <div style="margin-bottom: 15px; padding: 10px; background: #f3f4f6; border-radius: 8px;">
            <p><strong>Name:</strong> ${pharmacy.name}</p>
            <p><strong>Distance:</strong> ${pharmacy.distance} miles</p>
            <p><strong>Specialties:</strong> ${pharmacy.specialties.join(', ')}</p>
        </div>
    `).join('');
}

// ==================== TAB 2: Cluster Analysis ====================

function loadClusters() {
    fetch('/api/clusters')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('cluster-select');
            data.clusters.forEach(cluster => {
                const option = document.createElement('option');
                option.value = cluster;
                option.textContent = cluster;
                select.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading clusters:', error));
}

document.getElementById('analyze-cluster-btn').addEventListener('click', function() {
    const cluster = document.getElementById('cluster-select').value;

    if (!cluster) {
        alert('Please select a cluster');
        return;
    }

    fetch('/api/cluster_analysis', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cluster: cluster })
    })
    .then(response => response.json())
    .then(data => {
        displayClusterAnalysis(data);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error analyzing cluster. Please try again.');
    });
});

function displayClusterAnalysis(data) {
    const resultsSection = document.getElementById('cluster-results');
    resultsSection.style.display = 'block';

    // Display statistics
    document.getElementById('cluster-total').textContent = data.total_patients.toLocaleString();
    document.getElementById('cluster-avg').textContent = data.avg_distance.toFixed(2) + ' miles';
    document.getElementById('cluster-median').textContent = data.median_distance.toFixed(2) + ' miles';
    document.getElementById('cluster-max').textContent = data.max_distance.toFixed(2) + ' miles';

    // Create subgroup tabs
    const subgroupTabs = document.getElementById('subgroup-tabs');
    const subgroupContent = document.getElementById('subgroup-content');
    
    subgroupTabs.innerHTML = '';
    const subgroupKeys = Object.keys(data.subgroups);
    
    subgroupKeys.forEach((key, index) => {
        const button = document.createElement('button');
        button.className = 'subtab-btn' + (index === 0 ? ' active' : '');
        button.textContent = formatSubgroupName(key);
        button.onclick = () => showSubgroup(key, data.subgroups, button);
        subgroupTabs.appendChild(button);
    });

    // Show first subgroup by default
    if (subgroupKeys.length > 0) {
        showSubgroup(subgroupKeys[0], data.subgroups, document.querySelector('.subtab-btn'));
    }
}

function formatSubgroupName(name) {
    return name.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

function showSubgroup(key, subgroups, clickedButton) {
    // Update active button
    document.querySelectorAll('.subtab-btn').forEach(btn => btn.classList.remove('active'));
    if (clickedButton) clickedButton.classList.add('active');

    const content = document.getElementById('subgroup-content');
    const subgroupData = subgroups[key];

    content.innerHTML = `
        <h4>${formatSubgroupName(key)} Analysis</h4>
        <p class="muted">Click on a row to see the age distribution for that group.</p>
        <table style="width: 100%; margin-top: 15px;">
            <thead>
                <tr>
                    <th>${formatSubgroupName(key)}</th>
                    <th>Patient Count</th>
                    <th>Avg Distance (miles)</th>
                    <th>With Illness</th>
                    <th>Without Illness</th>
                </tr>
            </thead>
            <tbody>
                ${subgroupData.map((item, index) => `
                    <tr class="subgroup-row" data-key="${key}" data-index="${index}">
                        <td>${item.value}</td>
                        <td>${item.count.toLocaleString()}</td>
                        <td>${item.avg_distance}</td>
                        <td>${item.age_distribution ? item.age_distribution.with_illness_count.toLocaleString() : 'N/A'}</td>
                        <td>${item.age_distribution ? item.age_distribution.without_illness_count.toLocaleString() : 'N/A'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    // Add click listeners to rows
    document.querySelectorAll('.subgroup-row').forEach(row => {
        row.addEventListener('click', () => {
            const k = row.getAttribute('data-key');
            const i = parseInt(row.getAttribute('data-index'));
            const itemData = subgroups[k][i];
            if (itemData && itemData.age_distribution) {
                createAgeDistributionChart(itemData.age_distribution, itemData.value);
            }
            document.querySelectorAll('.subgroup-row').forEach(r => r.classList.remove('active'));
            row.classList.add('active');
        });
    });

    // Show chart for the first item by default
    if (subgroupData.length > 0 && subgroupData[0].age_distribution) {
        createAgeDistributionChart(subgroupData[0].age_distribution, subgroupData[0].value);
        document.querySelector('.subgroup-row').classList.add('active');
    }
}

function createAgeDistributionChart(data, subgroupValue) {
    const ctx = document.getElementById('cluster-chart').getContext('2d');
    if (clusterChart) {
        clusterChart.destroy();
    }

    clusterChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.ages,
            datasets: [
                {
                    label: 'With Chronic Illness',
                    data: data.with_illness,
                    borderColor: 'rgba(239, 68, 68, 0.8)',
                    backgroundColor: 'rgba(239, 68, 68, 0.2)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Without Chronic Illness',
                    data: data.without_illness,
                    borderColor: 'rgba(37, 99, 235, 0.8)',
                    backgroundColor: 'rgba(37, 99, 235, 0.2)',
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: `Patient Age Distribution for ${subgroupValue}`
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Patients'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Age'
                    }
                }
            }
        }
    });
}

// ==================== TAB 3: Pharmacy Deserts & Suggestions ====================

function initializeTab3() {
    loadPharmacyDeserts();
    loadPharmacySuggestions();
}

function initializeMap() {
    const mapEl = document.getElementById('map');
    if (!mapEl) return;
    if (!map) {
        map = L.map('map', {
            zoomControl: true,
            scrollWheelZoom: true
        }).setView([39.8283, -98.5795], 4); // Center of USA
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
    } else {
        map.invalidateSize();
    }
}

function loadPharmacyDeserts() {
    fetch('/api/pharmacy_deserts')
        .then(response => response.json())
        .then(data => {
            document.getElementById('desert-counties-count').textContent = data.desert_counties.length;
            document.getElementById('desert-patients-count').textContent = data.total_affected.toLocaleString();
            document.getElementById('desert-avg-distance').textContent = (data.avg_distance || 0).toFixed(2);
        })
        .catch(error => console.error('Error loading pharmacy deserts:', error));
}

function loadPharmacySuggestions() {
    fetch('/api/pharmacy_suggestions')
        .then(response => response.json())
        .then(data => {
            allSuggestions = (data.suggestions || []).map((s, idx) => ({ ...s, _index: idx }));
            window.pharmacySuggestions = allSuggestions; // keep global for markers/costs

            // Populate state filter
            const stateSelect = document.getElementById('state-filter');
            const states = Array.from(new Set(allSuggestions.map(s => (s.county.split(',')[1] || '').trim()).filter(Boolean))).sort();
            states.forEach(st => {
                const opt = document.createElement('option');
                opt.value = st; opt.textContent = st; stateSelect.appendChild(opt);
            });

            // Bind search, state and clear controls
            // Bind search and clear controls
            const search = document.getElementById('suggestion-search');
            const clearBtn = document.getElementById('clear-selections');
            const pagePrev = document.getElementById('page-prev');
            const pageNext = document.getElementById('page-next');
            const stateFilter = document.getElementById('state-filter');
            if (search) {
                search.addEventListener('input', () => applySuggestionFilters());
            }
            if (stateFilter) {
                stateFilter.addEventListener('change', () => applySuggestionFilters());
            }
            if (clearBtn) {
                clearBtn.addEventListener('click', () => clearAllSelections());
            }
            if (pagePrev && pageNext) {
                pagePrev.addEventListener('click', () => changePage(-1));
                pageNext.addEventListener('click', () => changePage(1));
            }

            // Initial render
            applySuggestionFilters();
        })
        .catch(error => console.error('Error loading suggestions:', error));
}

function displayPharmacySuggestions(pageItems) {
    const suggestionsGrid = document.getElementById('suggestions-list');
    if (!suggestionsGrid) return;

    if (pageItems.length === 0) {
        suggestionsGrid.innerHTML = '<p class="muted">No pharmacy deserts found based on the 20-mile rule.</p>';
        return;
    }

    suggestionsGrid.innerHTML = pageItems.map((suggestion) => {
        const checked = selectedIndices.has(suggestion._index) ? 'checked' : '';
        const selectedClass = selectedIndices.has(suggestion._index) ? ' selected' : '';
        return `
        <div class="suggestion-card${selectedClass}" data-index="${suggestion._index}" onclick="toggleSuggestion(${suggestion._index}, ${suggestion.latitude}, ${suggestion.longitude})">
            <input type="checkbox" class="suggestion-checkbox" data-index="${suggestion._index}" data-cost="${suggestion.estimated_cost}" ${checked} onclick="event.stopPropagation();">
            <div>
                <h4>📍 ${suggestion.county}</h4>
                <p class="muted"><strong>Patients:</strong> ${Number(suggestion.potential_patients || 0).toLocaleString()} • <strong>Distance:</strong> ${suggestion.avg_distance ? suggestion.avg_distance.toFixed(2) + ' mi' : 'N/A'}</p>
                <p class="cost">Est. Cost: $${Number(suggestion.estimated_cost || 0).toLocaleString()}</p>
            </div>
            <div>
                <button class="btn-primary btn-small" onclick="event.stopPropagation(); toggleSuggestion(${suggestion._index}, ${suggestion.latitude}, ${suggestion.longitude})">Highlight</button>
            </div>
        </div>`
    }).join('');

    // Add checkboxes event listeners
    document.querySelectorAll('.suggestion-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', updateCostCalculator);
    });

    updatePaginationIndicator();
}

function applySuggestionFilters() {
    const q = (document.getElementById('suggestion-search')?.value || '').toLowerCase();
    const state = (document.getElementById('state-filter')?.value || '').toLowerCase();
    filteredSuggestions = allSuggestions.filter(s => {
        const countyName = (s.county || '').toLowerCase();
        const statePart = (s.county.split(',')[1] || '').trim().toLowerCase();
        const matchesText = countyName.includes(q);
        const matchesState = !state || statePart === state;
        return matchesText && matchesState;
    });
    currentPage = 1;
    renderSuggestionPage();
}

function renderSuggestionPage() {
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    displayPharmacySuggestions(filteredSuggestions.slice(start, end));
}

function changePage(delta) {
    const totalPages = Math.max(1, Math.ceil(filteredSuggestions.length / pageSize));
    currentPage = Math.min(totalPages, Math.max(1, currentPage + delta));
    renderSuggestionPage();
}

function updatePaginationIndicator() {
    const indicator = document.getElementById('page-indicator');
    const totalPages = Math.max(1, Math.ceil(filteredSuggestions.length / pageSize));
    if (indicator) indicator.textContent = `Page ${currentPage} of ${totalPages} • ${filteredSuggestions.length} locations`;
}

function toggleSuggestion(index, lat, lon) {
    const card = document.querySelector(`.suggestion-card[data-index="${index}"]`);
    const checkbox = card.querySelector('.suggestion-checkbox');
    
    // Toggle selection
    const willSelect = !selectedIndices.has(index);
    if (willSelect) {
        selectedIndices.add(index);
        card.classList.add('selected');
        checkbox.checked = true;
    } else {
        selectedIndices.delete(index);
        card.classList.remove('selected');
        checkbox.checked = false;
    }
    
    // Update map marker
    updateMapMarker(index, lat, lon, willSelect);
    
    // Update cost
    updateCostCalculator();
}

function updateMapMarker(index, lat, lon, isSelected) {
    if (!map) {
        initializeMap();
    }

    // Remove existing marker for this index
    if (markers[index]) {
        map.removeLayer(markers[index]);
    }

    if (isSelected) {
        // Add marker
        const marker = L.marker([lat, lon], {
            icon: L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            })
        }).addTo(map);

        const suggestion = window.pharmacySuggestions[index];
        marker.bindPopup(`
            <strong>${suggestion.county}</strong><br>
            Patients: ${suggestion.potential_patients.toLocaleString()}<br>
            Cost: $${suggestion.estimated_cost.toLocaleString()}
        `);

        markers[index] = marker;

        // Fit to markers bounds
        const activeMarkers = Object.values(markers).filter(Boolean);
        if (activeMarkers.length > 1) {
            const group = L.featureGroup(activeMarkers);
            map.fitBounds(group.getBounds().pad(0.2));
        } else {
            map.setView([lat, lon], 6);
        }
    }
}

function updateCostCalculator() {
    let totalCost = 0;
    let selectedLocations = [];

    selectedIndices.forEach(index => {
        const s = window.pharmacySuggestions[index];
        if (!s) return;
        totalCost += parseInt(s.estimated_cost || 0);
        selectedLocations.push(s.county);
    });

    document.getElementById('total-cost').textContent = '$' + totalCost.toLocaleString();
    
    const selectedLocationsDiv = document.getElementById('selected-locations');
    if (selectedLocations.length > 0) {
        selectedLocationsDiv.innerHTML = `
            <p><strong>Selected Locations (${selectedLocations.length}):</strong></p>
            <ul style="margin-top: 10px;">
                ${selectedLocations.map(loc => `<li>${loc}</li>`).join('')}
            </ul>
        `;
    } else {
        selectedLocationsDiv.innerHTML = '<p>No locations selected</p>';
    }
}

function filterSuggestions(query) {
    query = (query || '').toLowerCase();
    const cards = document.querySelectorAll('.suggestion-card');
    cards.forEach(card => {
        const title = card.querySelector('h4')?.textContent.toLowerCase() || '';
        card.style.display = title.includes(query) ? '' : 'none';
    });
}

function clearAllSelections() {
    // Remove all markers for selected indices
    selectedIndices.forEach(index => {
        if (markers[index]) {
            map.removeLayer(markers[index]);
            markers[index] = null;
        }
    });
    selectedIndices.clear();

    // Update visible UI state
    document.querySelectorAll('.suggestion-card').forEach(card => card.classList.remove('selected'));
    document.querySelectorAll('.suggestion-checkbox').forEach(cb => cb.checked = false);

    updateCostCalculator();
}

// ==================== TAB 4: File Upload & Prediction ====================

function initializeTab4() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');

    // Click to browse
    browseBtn.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('click', () => fileInput.click());

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const file = e.dataTransfer.files[0];
        if (file && file.name.endsWith('.csv')) {
            handleFileUpload(file);
        } else {
            alert('Please upload a CSV file');
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFileUpload(file);
        }
    });
}

function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('file', file);

    // Show loading state
    const uploadArea = document.getElementById('upload-area');
    uploadArea.innerHTML = '<div class="loading"></div><p>Processing file...</p>';

    fetch('/api/predict_pharmacy', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            resetUploadArea();
        } else {
            displayUploadResults(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error uploading file. Please try again.');
        resetUploadArea();
    });
}

function resetUploadArea() {
    const uploadArea = document.getElementById('upload-area');
    const newInput = document.createElement('input');
    newInput.type = 'file';
    newInput.id = 'file-input';
    newInput.accept = '.csv';
    newInput.style.display = 'none';

    uploadArea.innerHTML = `
        <div class="upload-icon">📄</div>
        <p>Drag & drop your CSV file here or click to browse</p>
        <button id="browse-btn" class="btn-secondary">Browse Files</button>
    `;
    uploadArea.appendChild(newInput);

    // Re-bind events
    document.getElementById('browse-btn').addEventListener('click', () => newInput.click());
    uploadArea.addEventListener('click', () => newInput.click());
    uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('dragover'); });
    uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && file.name.endsWith('.csv')) handleFileUpload(file); else alert('Please upload a CSV file');
    });
    newInput.addEventListener('change', (e) => { const f = e.target.files[0]; if (f) handleFileUpload(f); });
}

function displayUploadResults(data) {
    const resultsSection = document.getElementById('upload-results');
    resultsSection.style.display = 'block';

    const stats = data.statistics;

    // Display basic statistics
    document.getElementById('upload-total').textContent = Number(stats.total_patients || 0).toLocaleString();
    document.getElementById('upload-avg-age').textContent = (Number(stats.avg_age || 0)).toFixed(1) + ' years';
    document.getElementById('upload-seniors').textContent = Number(stats.senior_count || 0).toLocaleString();
    document.getElementById('upload-pregnant').textContent = Number(stats.pregnant_count || 0).toLocaleString();

    // Display gender distribution chart
    if (stats.gender_distribution && Object.keys(stats.gender_distribution).length > 0) {
        createGenderChart(stats.gender_distribution);
    }

    // Display predictions table
    if (data.top_predictions && data.top_predictions.length > 0) {
        displayPredictionsTable(data.top_predictions);
        
        // Display probability statistics
        if (stats.avg_probability !== undefined) {
            document.getElementById('avg-probability').textContent = (stats.avg_probability * 100).toFixed(2) + '%';
        }
        if (stats.median_probability !== undefined) {
            document.getElementById('median-probability').textContent = (stats.median_probability * 100).toFixed(2) + '%';
        }
        
        // Display model status
        console.log('Model Status:', stats.model_status);
        if (stats.probability_distribution) {
            console.log('Probability Distribution:', stats.probability_distribution);
        }
    } else {
        const tbody = document.getElementById('predictions-tbody');
        if (!data.model_available) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #f59e0b;">⚠️ ML Model not loaded. Predictions unavailable.</td></tr>';
        } else if (stats.prediction_error) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: #ef4444;">❌ Prediction Error: ${stats.prediction_error}</td></tr>`;
        } else {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No predictions generated.</td></tr>';
        }
        
        // Clear probability stats
        document.getElementById('avg-probability').textContent = '--';
        document.getElementById('median-probability').textContent = '--';
    }

    // Reset upload area for new upload
    resetUploadArea();

    // Add or update download link if available
    if (data.statistics && data.statistics.download_url) {
        let dl = document.getElementById('download-link');
        if (!dl) {
            dl = document.createElement('div');
            dl.id = 'download-link';
            dl.style.marginTop = '12px';
            resultsSection.appendChild(dl);
        }
        dl.innerHTML = `<a class="btn-secondary" href="${data.statistics.download_url}" download>Download Predictions CSV</a>`;
    }
}



function createGenderChart(genderData) {
    const ctx = document.getElementById('gender-chart').getContext('2d');
    if (genderChart) {
        genderChart.destroy();
    }

    genderChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(genderData),
            datasets: [{
                data: Object.values(genderData),
                backgroundColor: [
                    'rgba(37, 99, 235, 0.8)',
                    'rgba(236, 72, 153, 0.8)',
                    'rgba(16, 185, 129, 0.8)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: { boxWidth: 10, boxHeight: 10, font: { size: 11 } }
                },
                title: {
                    display: true,
                    text: 'Gender Distribution',
                    font: { size: 12 }
                }
            }
        }
    });
}

function displayPredictionsTable(predictions) {
    const tbody = document.getElementById('predictions-tbody');
    
    tbody.innerHTML = predictions.map((pred) => {
        const probability = pred.probability;
        let probClass = 'probability-low';
        if (probability > 0.7) probClass = 'probability-high';
        else if (probability > 0.4) probClass = 'probability-medium';

        // Build detailed info tooltip/additional info
        let additionalInfo = [];
        if (pred.marital_status) additionalInfo.push(`${pred.marital_status}`);
        if (pred.is_senior_citizen) additionalInfo.push('Senior');
        if (pred.is_pregnant) additionalInfo.push('Pregnant');
        if (pred.has_chronic_illness) additionalInfo.push('Chronic Illness');
        
        const infoText = additionalInfo.length > 0 ? additionalInfo.join(', ') : 'N/A';

        return `
            <tr>
                <td>${pred.patient_id}</td>
                <td>${pred.age} / ${pred.gender}</td>
                <td class="${probClass}">${(probability * 100).toFixed(2)}%</td>
                <td>${pred.current_distance !== undefined ? pred.current_distance + ' mi' : 'N/A'}</td>
            </tr>
        `;
    }).join('');
}
