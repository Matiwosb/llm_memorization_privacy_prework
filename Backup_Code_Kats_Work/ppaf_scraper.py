import requests
from bs4 import BeautifulSoup
import json
import time
import os
import functions

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

#1 step
def main():
    ########### List of Google Play Store app data safety URLs to scrape, populates privacy policy txt file.
    ########## run this section by itself to get policy links ###################################
    # with open('data/privacy_policy_links.txt', 'a') as policy:
    #     with open('data/ds_urls.txt', 'r', encoding='utf-8') as file:
    #         for line in file:
    #             line = line.strip()
    #             # print(line)
    #             link, title = functions.get_link(line)  # get privacy policy link from google play page
    #             # print(link)
    #
    #             policy.write(f"{title}\n{link}\n")
    #             print(f"stored: {link}")

    ############################LOGIN TO PPAF########################################
    ############################ make sure the Privacify is up and running ###########
    ppafurl_auth = "http://localhost:5173/auth"  # login page for PPAF

    # path to chrome driver, change depending on OS
    # driver_path = "/Users/matiwosbirbo/.wdm/drivers/chromedriver/mac64/135.0.7049.42/chromedriver-mac-arm64/chromedriver"
    # service = Service(driver_path)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)  # selenium setup

    driver.get(ppafurl_auth)  # go to login page

    user = driver.find_element(By.XPATH, '//input[@placeholder="a.user@privacy.matters"]')  # finds username box
    password = driver.find_element(By.XPATH, '//input[@placeholder="Password"]')  # finds password box
    user.send_keys('test@g.com')  # Replace with the username you want to input
    password.send_keys("test123*")  # Replace with the password you want to input

    # submit form
    submit_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    submit_button.click()
    # this allows the page time to load, most errors come from the page not having enough time to load before the next action is taken.
    time.sleep(2)

    new_url = "http://localhost:5173/documents"  # The documents page URL to navigate to after login
    driver.get(new_url)  # This will redirect you to the new URL
    time.sleep(5)

    # ################################ SCRAPE DOCUMENT CARDS, block later############################
    # all_apps_data = {}
    # count = 0
    #
    # # get document ids from http://127.0.0.1:8000/docs, the Privacify API
    #
    # f = open('data/', encoding='utf-8')
    # data = json.load(f)
    #
    # for x in data:
    #     count += 1;
    #     # print(x['id']) #url ID
    #     driver.get(f"http://localhost:5173/documents/{x}")  # go to url
    #
    #     # os.makedirs("debug_html", exist_ok=True)
    #     #
    #     # with open(f"debug_html/page_{count}.html", "w", encoding='utf-8') as f:
    #     #     f.write(driver.page_source)
    #
    #     print(driver.current_url)  # check that we are at URL
    #     time.sleep(2)
    #
    #     page_html2 = driver.page_source  # collect HTML from page
    #     soup2 = BeautifulSoup(page_html2, 'html.parser')  # parse page
    #
    #     appid = soup2.find('h1', class_="m-8a5d1357 mantine-Title-root")  # find title
    #     app_id = appid.get_text(strip=True)  # e.g., "SnapChat"
    #     print(app_id)  # check card title
    #
    #     priv_data = {}  # current section data
    #     sections = soup2.find_all('div', class_='m-1b7284a3 mantine-Paper-root')  # find sections "Data shared, etc."
    #     sections = sections[:3]  # only use the first 3 sections of the card (data shared/ collected / security)
    #     for i in sections:
    #         header = i.find('h4', class_="m-8a5d1357 mantine-Title-root")  # get section title
    #         if header:
    #             title = header.get_text(strip=True)  # e.g., "Data shared"
    #             print(title)
    #             info = i.find('ul', class_="m-abbac491 mantine-List-root").get_text(strip=True)
    #             print(info)
    #
    #             priv_data[title] = info
    #
    #         all_apps_data[app_id] = priv_data
    #     functions.save_as_json(all_apps_data, 'data/ppaf_data.json')
    #     print(count)

        # 2 step
    ##################################### SCRAPE DOCUMENT END #######################################

    ################# FEED INTO PPAF ##################################
    with open("data/privacy_policy_links.txt", 'r') as file:
        lines = file.readlines()

        for i in range(0, len(lines), 2):  # Increment by 2 to grab pairs
            _id = lines[i].strip()  # Extract the ID (remove any extra spaces or newlines)
            _link = lines[i + 1].strip()  # Extract the link

            if "no policy" in _link: # skips apps that do not have policies available
                continue

            print(f"Processing ID: {_id}, Link: {_link}")

            id2 = driver.find_element(By.XPATH, '//input[@placeholder="Example Privacy Policy"]')  # find sections for submiting link and document name
            url = driver.find_element(By.XPATH, '//input[@placeholder="https://privacy.policies.matter"]')
            time.sleep(2)

            id2.send_keys(_id)
            url.send_keys(_link)
            time.sleep(3)
    # submit document for analysis
            submit_button = driver.find_element(By.XPATH, '//button[@type="submit"]')  # Or use By.ID, By.CLASS_NAME
            submit_button.click()
            time.sleep(100)  # time between submitting a new document.

            driver.refresh()  # refreshes page before submitting new document, old name sometimes get repeated if not.
            time.sleep(7)  # time for page to load, if number on documents is increasing up number in increments of 10.ß
    ######################################## FEED END ###################################################


if __name__ == '__main__':
    main()
