import pandas as pd
import json
import xml.etree.ElementTree as ET
import re

class SymptomsParser:
    def __init__(self, dict_file='symptoms_dict.json'):
        self.symptoms_dict = {}
        self.dict_file = dict_file
        self.load_dictionary()

    # Method to read data from multiple formats
    def read_data(self, file_path):
        if file_path.endswith('.csv'):
            data = pd.read_csv(file_path)
        elif file_path.endswith('.tsv'):
            data = pd.read_csv(file_path, delimiter='\t')
        elif file_path.endswith('.json'):
            data = pd.read_json(file_path)
        elif file_path.endswith('.xml'):
            data = self.parse_xml_to_dataframe(file_path)
        else:
            raise ValueError("Unsupported file format")
        return data

    # Custom XML parser to DataFrame
    @staticmethod
    def parse_xml_to_dataframe(file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()
        data = []
        for patient in root.findall('./Patient'):
            row = {}
            for child in patient:
                row[child.tag] = child.text
            data.append(row)
        return pd.DataFrame(data)

    # Method to enhance the dictionary by adding missing symptoms from the dataset
    def enhance_dictionary(self, data, symptom_col='Other_Symptoms'):
        # Loop through each row in the symptom column and extract symptoms
        for symptoms in data[symptom_col].dropna():
            # Split symptoms by comma (assuming multiple symptoms are comma-separated)
            for symptom in symptoms.split(','):
                symptom = symptom.strip()  # Remove any extra spaces
                
                # Check if this symptom is already in the dictionary
                found = False
                for symptom_group in self.symptoms_dict.values():
                    if symptom in symptom_group:
                        found = True
                        break

                # If not found, add it with default severities
                if not found:
                    symptom_key = f'Symptom{len(self.symptoms_dict) + 1}'
                    self.symptoms_dict[symptom_key] = {symptom: ['Mild', 'Low', 'High']}
        
        return self.symptoms_dict

    # Method to print the data based on the available columns in the dictionary
    def print_data_based_on_dict(self, data, symptom_col='Other_Symptoms'):
        available_symptoms = [symptom for group in self.symptoms_dict.values() for symptom in group]
        filtered_data = data[data[symptom_col].apply(lambda x: any(symptom in x for symptom in available_symptoms) if pd.notnull(x) else False)]
        print("Filtered Data Based on Available Symptoms in Dictionary:")
        print(filtered_data)

    # Method to dump the dictionary to a file
    def dump_dictionary(self):
        with open(self.dict_file, 'w') as f:
            json.dump(self.symptoms_dict, f, indent=4)
        print(f"Dictionary has been dumped to {self.dict_file}")

    # Method to load the dictionary from a file
    def load_dictionary(self):
        try:
            with open(self.dict_file, 'r') as f:
                self.symptoms_dict = json.load(f)
        except FileNotFoundError:
            print(f"No dictionary found at {self.dict_file}. Initializing with an empty dictionary.")
            self.symptoms_dict = {}

    # Method to update the dictionary after manual editing
    def manual_update(self):
        symptom = input("Enter the symptom you want to add: ")
        severity_levels = input("Enter severity levels (comma-separated, e.g., Mild, Low, High): ")
        severity_levels = [level.strip() for level in severity_levels.split(',')]
        
        # Check if symptom already exists
        symptom_exists = any(symptom in group for group in self.symptoms_dict.values())
        if symptom_exists:
            print(f"Symptom '{symptom}' already exists in the dictionary.")
        else:
            symptom_key = f'Symptom{len(self.symptoms_dict) + 1}'
            self.symptoms_dict[symptom_key] = {symptom: severity_levels}
            print(f"Added '{symptom}' with levels {severity_levels} to the dictionary.")
        self.dump_dictionary()

    # Main method to process the data
    def process_data(self, file_path, symptom_col='Other_Symptoms'):
        # Step 1: Read data
        data = self.read_data(file_path)

        # Step 2: Print data as per the available columns in the dictionary
        self.print_data_based_on_dict(data, symptom_col=symptom_col)

        # Step 3: Enhance dictionary with new symptoms found in the dataset
        self.enhance_dictionary(data, symptom_col=symptom_col)

        # Step 4: Reprint data based on the updated dictionary
        self.print_data_based_on_dict(data, symptom_col=symptom_col)

        # Step 5: Dump the enhanced dictionary to a file for manual editing
        self.dump_dictionary()

        


# Usage example:
if __name__ == "__main__":
    # Instantiate the parser
    parser = SymptomsParser(dict_file='symptoms_dict.json')

    # Process a data file (CSV, TSV, JSON, XML supported)
    file_path = 'data.csv'  # Replace with your actual file path
    parser.process_data(file_path, symptom_col='Other_Symptoms')
    choice = input("Do you want to manually update the dictionary : [Y,N]")
    if(choice == "Y"):
        parser.manual_update()
    else:
        pass