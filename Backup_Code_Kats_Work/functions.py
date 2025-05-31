import requests
from bs4 import BeautifulSoup
import json


# save data in json file
def save_as_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def scrape_data_safety(app_url):
    """
    :param app_url: URL from googleplay_urls.txt file.
    :return: data safety page info and application name.
    """
    # Helps with identification so the website doesn't automatically block it.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(app_url, headers=headers)  # send request to Google Play app page.

    if response.status_code == 200:  # check if page is up and available for scraping
        soup = BeautifulSoup(response.content, 'html.parser')  # gets raw HTML and parse it

        # Initialize an empty dictionary to store all sections
        data_safety_info = {}

        try:
            app_title = soup.find('div', class_="ylijCc").get_text(strip=True)  # grab app title & checks app is found, while page may return 200 web code, the application could not exist anymore.
        except AttributeError:
            print(f"Title not found, check if URL is valid:\nf{app_url}")
            exit()

        sections = soup.find_all('div', class_='Mf2Txd', jslog=True)  # Finds all sections

        # Iterate over each section and extract relevant data
        for section in sections:
            header = section.find('h2', class_='q1rIdc')
            if header:
                section_title = header.get_text(strip=True)  # e.g., "Data shared", "Data collected", etc.

                # Create a new entry for this section
                section_data = {}

                # Now find all subcategories within this section (e.g., "App interactions", "In-app search history")
                subcategories = section.find_all('div', class_='Vwijed')
                for subcategory in subcategories:
                    subcategory_title = subcategory.find('h3', class_='aFEzEb').get_text(strip=True)
                    subcategory_description = subcategory.find('div', class_='fozKzd').get_text(strip=True)

                    # Add the subcategory to the section
                    section_data[subcategory_title] = subcategory_description

                # Add the section to the main dictionary
                data_safety_info[section_title] = section_data

        return data_safety_info, app_title
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None


def collect_urls():
    """
    Accesses the Google Play Store and collects the URLS of applications using the search terms in the queries list.
    """
    base_url = "https://play.google.com"
    pages = []  # holds application URLs

    # array of search queries for apps
    
    queries = ["social", "games", "fitness", "entertainment", "messaging", "shopping", "music", "watch+tv", "tools",
               "food", "business", "photos", "videos", "communication", "productivity", "news", "travel", "maps",
               "budgeting", "audio", "banking", "home", "nutrition", "meditation", "sleep", "learning", "languages",
               "sports", "deals", "ride", "rental", "public+transit", "calendar", "organizer", "tracker", "camera",
               "editing", "animation", "art", "talk", "journal", "retail", "stocks", "education", "ecommerce", "beauty",
               "dating", "love", "community", "security", "healthcare", "therapy", "self-help", "outdoors", "bills",
               "streaming", "reading", "crypto", "workout", "events", "health", "charity", "parenting", "freelance",
               "fashion", "baking", "hobbies", "wellness", "adventure", "gift", "web", "gardening", "notes", "DIY",
               "photography", "cooking", "pets", "recipes", "mobile", "jobs", "projects", "gaming"]

    # collects the list of application urls found in each query.
    for term in queries:
        response = requests.get(f"{base_url}/store/search?q={term}&c=apps")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            app_links = soup.find_all('a', class_='Si6A0c Gy4nib')  # finds all applications in search page.

            for x in app_links:  # collects and save application URLs
                url = f"{base_url}{x.get('href')}"
                if url in pages:  # do not add any duplicate urls, since apps can fall under similar search terms
                    # print(url) # to see duplicate url
                    continue
                else:
                    pages.append(url)  # create list of URLs

    # saves the app URLs in a file, will overwrite previous information in file.
    with open("data/app_urls.txt", 'w') as url_page:
        for link in pages:
            url_page.write(f"{link}\n")

    print(f"Number of URLs collected:f{len(pages)}")

    # use URLs in pages list to find the data safety page url for that app, write to file.
    with open("data/ds_urls.txt", 'a') as ds_page:
        for link in pages:
            response2 = requests.get(link)

            if response2.status_code == 200:
                soup2 = BeautifulSoup(response2.content, 'html.parser')  # collect raw HTML and parse
                ds_link = soup2.find('a', class_="WpHeLc VfPpkd-mRLv6")  # find data safety link in HTML

                if ds_link:
                    full_link = f"{base_url}{ds_link.get('href')}"
                    ds_page.write(f"{full_link}\n")


def get_link(url):
    """
    :param url: data safety page URL
    :return: privacy policy linked to application and application name
    """
    global app_title, link
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/91.0.4472.124 Safari/537.36'
               # helps with identification so the website
               # doesn't automatically block it.
               }

    res = requests.get(url, headers=headers)  # send request to google play app

    if res.status_code == 200:
        soup = BeautifulSoup(res.content, 'html.parser')  # parse raw HTML
        app_title = soup.find('div', class_="ylijCc").get_text(strip=True)  # get app name
        policy = soup.find_all('a', class_='GO2pB')  # find policy link

        # for x in policy: # uncomment to check what is being scraped from the class element in policy.
        #     th = x.get("href")
        #     print(th)

        if len(policy) > 1:  # usually scrapes 2 things, the second element is the policy link.
            print(app_title)
            link = policy[1].get('href')
        else:
            link = f"no policy found for: {url}"

    return link, app_title

