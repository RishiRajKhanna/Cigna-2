import sys
import csv
from math import radians, sin, cos, sqrt, asin

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in miles between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3956 # Radius of earth in miles. Use 6371 for kilometers
    return c * r

def main():
    if len(sys.argv) != 4:
        print("Usage: python add_distance_to_pharmacy.py <patient_data_file> <pharmacy_data_file> <output_file>")
        return

    patient_data_file = sys.argv[1]
    pharmacy_data_file = sys.argv[2]
    output_file = sys.argv[3]

    try:
        with open(pharmacy_data_file, 'r', encoding='latin-1') as f:
            lines = f.readlines()
            header_line = lines[0].strip().replace('""', ' ').replace('"','')
            header = header_line.split(';')
            print(f"Header: {header}")
            lat_index = -1
            lon_index = -1
            for i, col in enumerate(header):
                if 'Y' in col:
                    lat_index = i
                if 'X' in col:
                    lon_index = i
            
            if lat_index == -1 or lon_index == -1:
                print("Could not find latitude or longitude columns in pharmacy data.")
                return

            pharmacies = []
            for line in lines[1:]:
                parts = line.strip().replace('""', ' ').replace('"','').split(';')
                if len(parts) > lat_index and len(parts) > lon_index:
                    try:
                        lat = float(parts[lat_index].replace(',', '.'))
                        lon = float(parts[lon_index].replace(',', '.'))
                        pharmacies.append((lat, lon))
                    except (ValueError, IndexError):
                        continue
    except FileNotFoundError:
        print(f"Error: Pharmacy data file not found at {pharmacy_data_file}")
        return
    except Exception as e:
        print(f"Error reading pharmacy data: {e}")
        return

    try:
        with open(patient_data_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', newline='', encoding='utf-8') as f_out:
            patient_reader = csv.reader(f_in)
            writer = csv.writer(f_out)

            header = next(patient_reader)
            writer.writerow(header + ['distance_to_nearest_pharmacy_miles'])

            for i, row in enumerate(patient_reader):
                if len(row) > 9:
                    try:
                        patient_lat = float(row[8])
                        patient_lon = float(row[9])
                    except (ValueError, IndexError):
                        row.append('')
                        writer.writerow(row)
                        continue

                    min_distance = float('inf')
                    for pharm_lat, pharm_lon in pharmacies:
                        distance = haversine(patient_lat, patient_lon, pharm_lat, pharm_lon)
                        if distance < min_distance:
                            min_distance = distance
                    
                    if min_distance > 10:
                        row.append(round(min_distance, 2))
                    else:
                        row.append('') # Or 0, or some other indicator

                writer.writerow(row)
                if (i + 1) % 100 == 0:
                    print(f"Processed {i+1} rows...")

        print(f"Successfully created the file with distance to nearest pharmacy: {output_file}")

    except FileNotFoundError:
        print(f"Error: Patient data file not found at {patient_data_file}")
        return
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()