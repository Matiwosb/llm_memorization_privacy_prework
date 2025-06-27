import functions_with_description
import re # Import the re module for regular expressions

# description_llm_keywords =["AI-powered", "AI-driven", "AI-based", "AI-enhanced", "AI-assisted", "AI-enabled", "Artificial Intelligence", "Machine Learning", "ML-powered", "ML-driven", "ML-based", "ML-enhanced", "ML-assisted", "ML-enabled"]
# description_llm_keywords =["AI-powered", "GPT-4", "GPT-3.5", "GPT-3", "ChatGPT", "LLM", "Large Language Model", "Generative AI", "AI-driven", "AI-based", "AI-enhanced", "AI-assisted", "AI-enabled", "Artificial Intelligence", "Machine Learning", "ML-powered", "ML-driven", "ML-based", "ML-enhanced", "ML-assisted", "ML-enabled"]
description_llm_keywords =["AI-powered", "GPT", "ChatGPT", "Claude", "Gemini", "LLaMA", "Mistral",
                           "LLM", "language model", "transformer model"]

# review_llm_keywords = ["GPT", "AI assistant", "AI chatbot", "AI-writer", "language model", "ChatGPT", "AI picture generator", "AI", "Artificial Intelligence", "AI avatar maker", "AI photo generator", "AI avatars", "AI art", "AI-Driven", "AI video"]
review_llm_keywords = ["GPT", "AI assistant", "AI chatbot", "AI-writer", "language model", "ChatGPT"]
def main():
    # Ensure the 'data' directory exists
    # if not os.path.exists
    ######### ONLY NEEDS TO BE RUN TO POPULATE THE 'googleplay_urls.txt' FILE, keep commented out otherwise. ###########
    functions_with_description.collect_urls()

    # Initialize an empty dictionary to store all apps' data.
    all_apps_data = {}
    
    app_count = 0  # Initialize a counter for processed apps
    max_apps_to_process = 20  # Set the maximum number of apps to process for testing

    # Opens "ds_urls.txt" file and loops through each app url in the file.
    with open('data/gs_urls_v2.txt', 'r') as file:
        for line in file:
            if app_count >= max_apps_to_process:
                break  # Exit the loop once the desired number of apps have been processed

            line = line.strip()  # Remove any leading or trailing whitespace.

            # Extract app_id from the URL (e.g., 'com.example.app')
            # This regex assumes the app_id is in the format id=com.package.name
            app_id_match = re.search(r'id=([^&]+)', line)
            app_id = app_id_match.group(1) if app_id_match else None

            if app_id:
                # Scrape the data safety information
                data_safety, app_title = functions_with_description.scrape_data_safety(line)
                
                # Get the app description using the new function
                description = functions_with_description.get_app_description(app_id)

                # Analyze the description for LLM-related keywords
                llm_indicator_in_description = []
                if description and description != 'N/A':
                    llm_indicator_in_description = functions_with_description.find_llm_keywords(
                        description, 
                        description_llm_keywords
                    )


                # Get the app review using the new function
                reviews = functions_with_description.get_app_reviews(app_id)

                processed_reviews_with_llm_analysis = []
                if reviews:
                    for review_dict in reviews:
                        if not isinstance(review_dict, dict):
                            print(f"Warning: Skipping non-dictionary review list: {type(review_dict)}")
                            continue

                        # Analyze the reviews for LLM-related keywords
                        review_content = review_dict.get("content", " ")
                        llm_indicator_in_review = []
                        if review_content:
                            llm_indicator_in_review = functions_with_description.find_llm_keywords(
                                review_content,
                                review_llm_keywords
                            )

                        # Add the LLM analysis to the review dictionary
                        review_dict["llm_review_indicator"] = llm_indicator_in_review
                        processed_reviews_with_llm_analysis.append(review_dict)


                if app_title: # Ensure app_title was successfully scraped
                    print(f"Processing {app_title} (ID: {app_id})...")

                    # # Store the combined data in the dictionary
                    # all_apps_data[app_title] = {
                    #     "description": description,
                    #     "data_safety": data_safety
                    # }
                    app_entry = {
                        "description": description,
                        "llm_indicator_in_description": llm_indicator_in_description,
                        "data_safety": data_safety,
                        # "reviews": reviews,
                        # "llm_indicator_in_review": processed_reviews_with_llm_analysis
                        # "reviews": processed_reviews_with_llm_analysis
                    }

                    consolidated_review_keywords = set()
                    for review in processed_reviews_with_llm_analysis:
                        if "llm_review_indicator" in review and review["llm_review_indicator"]:
                            for keyword in review["llm_review_indicator"]:
                                consolidated_review_keywords.add(keyword)

                    app_entry["llm_indicator_in_review_summary"] = sorted(list(consolidated_review_keywords))

                    all_apps_data[app_title] = app_entry
                    app_count += 1  # Increment the counter only for successfully processed apps
                else:
                    print(f"Skipping URL due to missing app title: {line}")
            else:
                print(f"Could not extract app ID from URL: {line}")

    # Save the combined data to a JSON file.
    functions_with_description.save_as_json(all_apps_data, 'data/gp_data_safety_with_description_v2.json')
    print(f"Data for {app_count} apps with descriptions saved to gp_data_safety_with_description_v2.json")


if __name__ == '__main__':
    main()