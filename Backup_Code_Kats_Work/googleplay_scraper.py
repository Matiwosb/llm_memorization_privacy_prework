import functions


def main():
    ######### ONLY NEEDS TO BE RUN TO POPULATE THE 'googleplay_urls.txt' FILE, keep commented out otherwise. ###########
    # functions.collect_urls()

    # Initialize an empty dictionary to store all apps' data.
    all_apps_data = {}

    # Opens "googleplay_urls.txt" file and loops through each app url in the file.
    with open('data/ds_urls.txt', 'r') as file:
        for line in file:
            line = line.strip()  # Remove any leading or trailing whitespace.

            # Scrape the data safety information from the application. Returns a dictionary of the data safety information and the application name.
            data_safety, app_id = functions.scrape_data_safety(line)
            print(f"Scraping data safety information for {app_id}...")

            # Store the application entry in the all_apps dictionary.
            all_apps_data[app_id] = data_safety

    # Save the combined data to a JSON file.
    functions.save_as_json(all_apps_data, 'data/gp_data_safety.json')
    print("Data saved to gp_data_safety.json")


if __name__ == '__main__':
    main()
