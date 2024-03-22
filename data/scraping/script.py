import requests
from bs4 import BeautifulSoup
import json

state_codes = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

for state_name in state_codes:

    url = f"https://www.wildflower.org/collections/printable.php?collection={state_name}"

    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', style="width:100%;")

    species_list = []

    # Check if the table was found
    if table:
        rows = table.find_all('tr')[1:]  # Skipping header row
        for row in rows:
            cols = row.find_all('td')
            species = {
                'Scientific Name': cols[0].text.strip(),
                'Common Name': cols[1].text.strip(),
                'Duration': cols[2].text.strip(),
                'Habit': cols[3].text.strip(),
                'Sun': cols[4].text.strip(),
                'Water': cols[5].text.strip(),
            }
            species_list.append(species)

        output_file = f"{state_name}_species_list.json"

        # Write the species list to a JSON file
        with open(output_file, "w") as file:
            json.dump(species_list, file, indent=4)


#Unable to do it due to the cloudflare restrictions i can only load the first page with the cloudflare notification and the rest of the pages are blocked by cloudflare