import functions_with_description
import re # Import the re module for regular expressions
import json
import cohere
import time

# Initialize the Cohere client with your API key
cohere_client = cohere.Client("YOUR_COHERE_API_KEY")  # Replace with your actual Cohere API key

# Keywords to identify LLMs in app descriptions and reviews
description_and_review_llm_keywords =["AI-powered", "GPT", "ChatGPT", "Claude", "Gemini", "LLaMA", "Mistral","LLM", "language model", 
                           "transformer model", "GPT-4", "GPT-3.5", "GPT-3", "DeepSeek V3", "DeepSeek R1", "GPT-4o", 
                           "Gemini Pro 1.5", "Claude", "AI assistant", "AI chatbot", "AI writer", "AI-driven",
                           "AI-based", "AI-enhanced", "AI-enabled", "AI picture generator", "AI avatar maker",
                           "AI photo generator", "AI avatars", "AI art", "AI-Driven", "AI video", "Generative AI"]

def main():
    # Ensure the 'data' directory exists
    # if not os.path.exists
    ######### ONLY NEEDS TO BE RUN TO POPULATE THE 'googleplay_urls.txt' FILE, keep commented out otherwise. ###########
    functions_with_description.collect_urls()

    # Initialize an empty dictionary to store all apps' data.
    all_apps_data = {}
    
    # app_count = 0  # Initialize a counter for processed apps
    # max_apps_to_process = 20  # Set the maximum number of apps to process for testing

    # Opens "ds_urls.txt" file and loops through each app url in the file.
    with open('data/gs_urls_v4.txt', 'r') as file:
        for line in file:
            # if app_count >= max_apps_to_process:
            #     break  # Exit the loop once the desired number of apps have been processed

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

                # Cohere
                cohere_llm_type = functions_with_description.classify_llm_with_cohere(description, cohere_client)
                time.sleep(6.5)


                cohere_only_mobile = functions_with_description.detect_mobile_only_with_cohere(description, cohere_client)
                time.sleep(6.5)

                # Analyze the description for LLM-related keywords
                llm_indicator_in_description = []
                if description and description != 'N/A':
                    llm_indicator_in_description = functions_with_description.find_llm_keywords(
                        description, 
                        description_and_review_llm_keywords
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
                                description_and_review_llm_keywords
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
                        "app_id": app_id,
                        "description": description,
                        "llm_indicator_in_description": llm_indicator_in_description,
                        "data_safety": data_safety,
                        "cohere_llm_type": cohere_llm_type,
                        "cohere_only_mobile": cohere_only_mobile,
                    }

                    consolidated_review_keywords = set()
                    for review in processed_reviews_with_llm_analysis:
                        if "llm_review_indicator" in review and review["llm_review_indicator"]:
                            for keyword in review["llm_review_indicator"]:
                                consolidated_review_keywords.add(keyword)

                    app_entry["llm_indicator_in_review_summary"] = sorted(list(consolidated_review_keywords))

                    all_apps_data[app_title] = app_entry
                    # app_count += 1  # Increment the counter only for successfully processed apps
                else:
                    print(f"Skipping URL due to missing app title: {line}")
            else:
                print(f"Could not extract app ID from URL: {line}")

    # Save the combined data to a JSON file.
    functions_with_description.save_as_json(all_apps_data, 'data/gp_data_safety_with_description_v4.json')
    # print(f"Data for {app_count} apps with descriptions saved to gp_data_safety_with_description_v4.json")
    # print(f"Apps with descriptions saved to gp_data_safety_with_description_v4.json")
    # Print the number of apps saved
    print(f"{len(all_apps_data)} apps data saved to gp_data_safety_with_description_v4.json")

# ____________Filter for mobile apps and output summary and save to json file____________
    mobile_apps_summary = []
    for app_title, app_info in all_apps_data.items():
        description = app_info.get("description", "").lower()
        cohere_llm_type = app_info.get("cohere_llm_type", "None.")
        app_id = app_info.get("app_id", None)

        # Heuristic checks for mobile apps
        if any(mobile_word in description for mobile_word in ["mobile", "phone", "phone app", "android", "smartphone"]):
            #extract llm types
            llm_apps = functions_with_description.find_llm_keywords(description, description_and_review_llm_keywords)

            # #Extract app_id from app_info if possible
            # app_id = app_info.get("app_id", None)
            # if "reviews" in app_info and app_info["reviews"]:
            #     review = app_info["reviews"][0]
            #     match = re.search(r'id=([-zA-Z0-9_.]+)', review.get("reviewId", ""))
            #     if match:
            #         app_id = match.group(1)

            
            app_link = f"https://play.google.com/store/apps/details?id={app_id}" if app_id else "N/A"

            mobile_apps_summary.append({
                "app_name": app_title,
                "app_link": app_link,
                "llm_types_detected": llm_apps,
                "cohere_llm_type": cohere_llm_type
            })

    # Save the mobile apps summary to a JSON file
    with open('data/mobile_apps_summary_v4.json', 'w') as summary_file:
        json.dump(mobile_apps_summary, summary_file, indent=4) #used for testing reasons

    print(f"Saved {len(mobile_apps_summary)} mobile apps using LLMs to data/mobile_apps_summary_v4.json")

if __name__ == '__main__':
    main()