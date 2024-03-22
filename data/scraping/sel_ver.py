from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time
import random

# Initialize a Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

state_codes = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]
additional_state_codes = ["CA_north", "CA_south", "FL_north", "FL_central", "FL_south", "TX_east", "TX_central", "TX_northcentral", "TX_south", "TX_west", "TX_highplains"]

# Iterate through each state
for state_name in state_codes:
    url = f"https://www.wildflower.org/collections/printable.php?collection={state_name}"
    driver.get(url)

    # Wait for JavaScript to render the content, adjust the sleep time as necessary
    random_sleep = random.randint(5, 10)
    time.sleep(90 +random_sleep)  # Adjust this sleep time based on your internet speed and page complexity
    
    # Now you can use BeautifulSoup to parse the page source
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Assuming you've found the correct table as before
    table = soup.find('table', style="width:100%;")
    species_list = []

    if table:
        rows = table.find_all('tr')[1:]  # Skipping the header row
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

        # Save to a JSON file
        with open(f"{state_name}_species_list.json", "w") as file:
            json.dump(species_list, file, indent=4)

        print(f"Data for {state_name} saved.")

# Don't forget to close the driver
driver.quit()