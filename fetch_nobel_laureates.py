import requests
import json
import csv
import logging

field_names = ['id', 'name', 'dob', 'unique_prize_years', 'unique_prize_categories', 'gender', 'born_country']
laureates_url = 'https://api.nobelprize.org/v1/laureate.json'
countries_url = 'https://api.nobelprize.org/v1/country.json'

logging.basicConfig(filename='fetch_nobel.log', level=logging.INFO)

def fetch_data_from_url(url):
    try:
        obj_data = requests.get(url)
        obj_data.raise_for_status()  # Raise an exception if the request was not successful
        obj_json = obj_data.json()
        return obj_json
    except requests.exceptions.RequestException as err:
        logging.error("Error fetching data from URL: %s", err)
        raise

def generate_lookup(countries_list):
    born_countries_lookup = {}
    for country in countries_list:
        try:
            born_countries_lookup[country['code']] = country['name']
        except KeyError:
            logging.error("Error with country: %s", country)
    return born_countries_lookup

def extract_values_laureates(laureate, born_countries_lookup):
    try:
        laureate_row = {}
        laureate_row['id'] = laureate['id']
        if laureate['surname'] is not None:
            laureate_row['name'] = laureate['firstname'] + ' ' + laureate['surname']
        else:
            laureate_row['name'] = laureate['firstname']
        laureate_row['dob'] = laureate['born']
        prize_years = set()
        prize_categories = set()
        for prize in laureate['prizes']:
            prize_years.add(prize['year'])
            prize_categories.add(prize['category'])

        laureate_row['unique_prize_years'] = ';'.join(prize_years)
        laureate_row['unique_prize_categories'] = ';'.join(prize_categories)
        laureate_row['gender'] = laureate['gender']
        laureate_row['born_country'] = born_countries_lookup[laureate['bornCountryCode']]
        return laureate_row
    except Exception as err:
        logging.error("Error loading laureate: %s", err)
        raise

def fetch_nobel_laureates():
    try:
        # Fetch data from the APIs
        laureates_list = fetch_data_from_url(laureates_url)["laureates"]
        countries_list = fetch_data_from_url(countries_url)["countries"]

        # Generate the lookup
        born_countries_lookup = generate_lookup(countries_list)

        # Extract values from every laureate row
        result = []
        for laureate in laureates_list:
            laureate_row = extract_values_laureates(laureate, born_countries_lookup)
            result.append(laureate_row)

        # Writing the results to a CSV file
        with open('solution_laureates.csv', 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(result)
    except Exception as err:
        logging.error("An error occurred: %s", err)
        raise

if __name__ == '__main__':
    fetch_nobel_laureates()
