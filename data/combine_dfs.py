import pandas as pd
import json
from pathlib import Path

user_data = {
    "location": "AL",
    "gardenSize": "small",
    "existingPlants": [],
    "shade": "Part Shade",
    "soilType": "clay",
    "water": "Moist"
}
location = user_data['location']
gardensize = user_data['gardenSize']
existing_plants=user_data["existingPlants"]
shade =  user_data["shade"]
soil = user_data["soilType"]
water = user_data["water"]
json_dir = Path("scraped_data")
dfs = []
for file in json_dir.glob("*_species_list.json"):
    # Extract the state code from the file name
    state_code = file.stem.split('_')[0]
    
    # Load the JSON content
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create a DataFrame from the JSON data
    df = pd.DataFrame(data)
    
    # Add a column for the state code
    df['State Code'] = state_code
    
    # Append the DataFrame to the list
    dfs.append(df)

# Concatenate all DataFrames in the list into a single DataFrame
all_species_df = pd.concat(dfs, ignore_index=True)

# Save the DataFrame as a CSV file
all_species_df.to_csv('output.csv', index=False)