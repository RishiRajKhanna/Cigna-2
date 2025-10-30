import sys
import csv

def main():
    if len(sys.argv) != 4:
        print("Usage: python add_pharmacy_desert_column.py <patient_data_file> <pharmacy_data_file> <output_file>")
        return

    patient_data_file = sys.argv[1]
    pharmacy_data_file = sys.argv[2]
    output_file = sys.argv[3]

    try:
        with open(pharmacy_data_file, 'r', encoding='latin-1') as f:
            lines = f.readlines()
            header = lines[0].strip().replace('"', '').split(';')
            county_index = header.index('COUNTY')
            state_index = header.index('STATE')

            pharmacy_locations = set()
            for line in lines[1:]:
                parts = line.strip().replace('"', '').split(';')
                if len(parts) > county_index and len(parts) > state_index:
                    county = parts[county_index].lower()
                    state = parts[state_index].lower()
                    pharmacy_locations.add((county, state))

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
            writer.writerow(header + ['is_pharmacy_desert'])

            for row in patient_reader:
                if len(row) > 7:
                    county = row[6].lower()
                    state = row[7].lower()

                    if (county, state) in pharmacy_locations:
                        row.append('No')
                    else:
                        row.append('Yes')
                writer.writerow(row)
        print(f"Successfully created the file with pharmacy desert information: {output_file}")

    except FileNotFoundError:
        print(f"Error: Patient data file not found at {patient_data_file}")
        return
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()