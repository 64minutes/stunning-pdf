import os
import time
import json
from selenium import webdriver
import csv
import pandas as pd


def read_csv():
    with open('data.csv', 'r') as file:
        df = pd.read_csv(file)
        links = df['Official Websites'].dropna()
        sources = []
        for link in links:
            sources.append(link)
        print(sources)
        return sources


def create_data():
    with open('data.csv', 'r') as file:
        df = pd.read_csv(file)

        #Extract columns
        official_links = df['Official Websites']
        unofficial_links = df['Unofficial Websites']
       
        #Initialise lists
        cleaned_official_links = []
        cleaned_unofficial_links = []
        consolidated_links = []

        # Collapse multiple links in tab into a list
        for link in official_links:
            cleaned_official_links.append(str(link).split("\n"))
        for link in unofficial_links:
            cleaned_unofficial_links.append(str(link).split("\n"))

        #Consolidate official and unoffical links into a single list 
        for _ in range(len(cleaned_official_links)):
            consolidated_links.append({
                'Official Links': cleaned_official_links[_],
                'Unofficial Links': cleaned_unofficial_links[_],
            })

        #Create dictionary of name (key) and their assiociated links (value)
        df['Links'] = consolidated_links
        my_dict = df.set_index('Full Name').to_dict()['Links']
        return my_dict


def main():
    people = read_csv()
    appState = {
        "recentDestinations": [
            {
                "id": "Save as PDF",
                "origin": "local"
            }
        ],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }

    profile = {'printing.print_preview_sticky_settings.appState': json.dumps(appState)}

    download_path = r'C:\Users\User\Downloads' # Path where browser save files
    new_path = r'C:\Users\User\Documents\Lyodssoft Work\save_pdf\output' # Path where to move file

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('prefs', profile)
    chrome_options.add_argument('--kiosk-printing')
    driver = webdriver.Chrome(options=chrome_options)

    for website in sources:
        driver.get(website)
        time.sleep(5)
        driver.execute_script('window.print();')

        # new_filename = f'{website}.pdf' # Set the name of file
        timestamp_now = time.time() # time now
        # # Now go through the files in download directory
        for (dirpath, dirnames, filenames) in os.walk(download_path):
            for filename in filenames:
                if filename.lower().endswith(('.pdf')):
                    full_path = os.path.join(download_path, filename)
                    try:
                        timestamp_file = os.path.getmtime(full_path) # time of file creation
                    except FileNotFoundError:
                        pass
                    # if time delta is less than 15 seconds move this file
                    else:
                        if (timestamp_now - timestamp_file) < 15: 
                            full_new_path = os.path.join(new_path, filename)
                            os.rename(full_path, full_new_path)
                            print(full_path+' is moved to '+full_new_path)


if __name__ == "__main__":
    create_data()