import os
import time
import json
from selenium import webdriver
import csv
import pandas as pd
PARENT_DIR = 'insert parent dir"
DOWNLOAD_PATH = "insert download path"

def main():
    global PARENT_DIR
    global DOWNLOAD_PATH
    #Setting up automated Chrome to save pdf
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
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('prefs', profile)
    chrome_options.add_argument('--kiosk-printing')
    driver = webdriver.Chrome(options=chrome_options)

    #Creating address book of person: links
    pages = create_links_pages()
    #Create dir for every person
    create_dir(pages)

    #Iterating over dict object of address book of person: links
    for person, links in pages.items():
        #path pointing to person's own directory
        print(f"Looping over {person}")
        person_path = os.path.join(PARENT_DIR, person)
        #creating paths to official links & unofficial links in person's own directory
        official_links_dir = os.path.join(person_path, "Official Links")
        unofficial_links_dir = os.path.join(person_path, "Unofficial Links")
        try:
            os.mkdir(official_links_dir)
            os.mkdir(unofficial_links_dir)
        except FileExistsError:
            pass
        #Iterating over person's official links aka primary sources
        official_links = links['Official Links']
        print(official_links)
        for link in official_links:
            try:
                take_screenshot(link=link, output_dir=official_links_dir, driver=driver)
            except:
                print(f"{link} did not print for {person}")
        unofficial_links = links['Unofficial Links']
        print(unofficial_links)
        for link in unofficial_links:
            try:
                take_screenshot(link=link, output_dir=unofficial_links_dir, driver=driver)
            except:
                print(f"{link} did not print for {person}")


def create_links_pages():
    """Opens a file named "data.csv", creates a dict object relating a person with their primary/secondary/tetiary sources"""
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
        df = df.dropna(subset=['Full Name', 'Official Websites', 'Unofficial Websites'])
        links_pages = df.set_index('Full Name').to_dict()['Links']
        return links_pages


def create_dir(links_pages):
    """Takes in the dict object of person:sources and makes folders of all people in the dict on local disk drive"""
    people = links_pages.keys()
    global PARENT_DIR
    for person in people:
        directory = person
        path = os.path.join(PARENT_DIR, directory)
        try:        
            os.mkdir(path)
        except FileExistsError:
            pass


def take_screenshot(link, output_dir, driver):
    time.sleep(3)
    global DOWNLOAD_PATH
    download_path = DOWNLOAD_PATH
    driver.get(link)
    time.sleep(5)
    driver.execute_script('window.print();')
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
                    if (timestamp_now - timestamp_file) < 10: 
                        full_new_path = os.path.join(output_dir, filename)
                        os.rename(full_path, full_new_path)
                        print(full_path+' is moved to '+full_new_path)


if __name__ == "__main__":
    main()
