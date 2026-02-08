import functions_with_description
import re
import json
import cohere
import time
import os
import datetime
import sys

# Initialize the Cohere client with your API key
cohere_client = cohere.Client("") # Remember to replace with your actual Cohere API key

# Keywords to identify LLMs in app descriptions and reviews
description_and_review_llm_keywords =["AI-powered", "GPT", "ChatGPT", "Claude", "Gemini", "LLaMA", "Mistral","LLM", "language model",
                           "transformer model", "GPT-4", "GPT-3.5", "GPT-3", "DeepSeek V3", "DeepSeek R1", "GPT-4o",
                           "Gemini Pro 1.5", "Claude", "AI assistant", "AI chatbot", "AI writer", "AI-driven",
                           "AI-based", "AI-enhanced", "AI-enabled", "AI picture generator", "AI avatar maker",
                           "AI photo generator", "AI avatars", "AI art", "AI-Driven", "AI video", "Generative AI"]

# Custom class to tee output to both console and file
class Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush() # Ensure immediate writing
    def flush(self):
        for f in self.files:
            f.flush()

def main():
    # Setup for timestamped output
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"data/analysis_output_{timestamp}.txt"

    # Ensure the 'data' directory exists
    if not os.path.exists('data'):
        os.makedirs('data')

    # Open the file for writing
    log_file = open(output_filename, 'w')

    # Redirect print statements to both console and file
    original_stdout = sys.stdout # Store original stdout
    sys.stdout = Tee(original_stdout, log_file) # Use our custom Tee class

    print(f"Analysis started at: {datetime.datetime.now()}")
    print("-" * 50)

    functions_with_description.collect_urls() # Uncomment if you need to re-collect URLs

    all_apps_data = {} # Stores all scraped data for all apps

    # Lists to store apps for specific JSON outputs
    ai_integrated_by_keywords_overall_list = []
    ai_integrated_by_cohere_overall_list = []
    ai_integrated_by_keywords_mobile_list = []
    ai_integrated_by_cohere_mobile_list = []

    total_apps_processed = 0

    with open('data/gs_urls_v4.txt', 'r') as file:
        for line in file:
            line = line.strip()
            app_id_match = re.search(r'id=([^&]+)', line)
            app_id = app_id_match.group(1) if app_id_match else None

            if app_id:
                total_apps_processed += 1

                data_safety, app_title = functions_with_description.scrape_data_safety(line)
                description = functions_with_description.get_app_description(app_id)

                # Cohere Classification for LLM type (AI-integrated by Cohere)
                cohere_llm_type = functions_with_description.classify_llm_with_cohere(description, cohere_client)
                time.sleep(1) # Add a small delay to avoid hitting rate limits

                # Commenting out Cohere Mobile Detection as requested
                cohere_only_mobile_status = "N/A (Cohere Mobile Detection Commented Out)" # Placeholder value

                # Analyze description for LLM-related keywords (AI-integrated by Keywords)
                llm_indicator_in_description = []
                if description and description != 'N/A':
                    llm_indicator_in_description = functions_with_description.find_llm_keywords(
                        description,
                        description_and_review_llm_keywords
                    )

                reviews = functions_with_description.get_app_reviews(app_id)
                processed_reviews_with_llm_analysis = []
                consolidated_review_keywords = set()
                if reviews:
                    for review_dict in reviews:
                        if not isinstance(review_dict, dict):
                            print(f"Warning: Skipping non-dictionary review list: {type(review_dict)}")
                            continue
                        review_content = review_dict.get("content", " ")
                        llm_indicator_in_review = functions_with_description.find_llm_keywords(
                            review_content,
                            description_and_review_llm_keywords
                        )
                        review_dict["llm_review_indicator"] = llm_indicator_in_review
                        processed_reviews_with_llm_analysis.append(review_dict)

                        if llm_indicator_in_review:
                            for keyword in llm_indicator_in_review:
                                consolidated_review_keywords.add(keyword)

                if app_title:
                    print(f"Processing {app_title} (ID: {app_id})...")

                    # Store all scraped data for this app
                    app_entry = {
                        "app_id": app_id,
                        "app_name": app_title,
                        "app_link": f"https://play.google.com/store/apps/details?id={app_id}",
                        "description": description,
                        "llm_indicator_in_description": llm_indicator_in_description,
                        "llm_indicator_in_review_summary": sorted(list(consolidated_review_keywords)),
                        "data_safety": data_safety,
                        "cohere_llm_type": cohere_llm_type,
                        "cohere_only_mobile_status": cohere_only_mobile_status # This will show the placeholder
                    }
                    all_apps_data[app_title] = app_entry

                    # --- Determine AI-Integrated Status (Overall) ---
                    is_ai_by_keywords = bool(llm_indicator_in_description) or bool(consolidated_review_keywords)
                    is_ai_by_cohere = (cohere_llm_type not in ["None", "No description", "Cohere failed"])

                    # Populate overall AI-integrated lists for JSON output
                    if is_ai_by_keywords:
                        ai_integrated_by_keywords_overall_list.append({
                            "app_name": app_title,
                            "app_id": app_id,
                            "app_link": f"https://play.google.com/store/apps/details?id={app_id}",
                            "llm_keywords_detected": sorted(list(set(llm_indicator_in_description + list(consolidated_review_keywords))))
                        })
                    if is_ai_by_cohere:
                        ai_integrated_by_cohere_overall_list.append({
                            "app_name": app_title,
                            "app_id": app_id,
                            "app_link": f"https://play.google.com/store/apps/details?id={app_id}",
                            "cohere_llm_type": cohere_llm_type
                        })

                    # --- Determine Mobile Status using Keywords ---
                    description_lower = description.lower()
                    is_mobile_by_keywords = any(mobile_word in description_lower for mobile_word in ["mobile", "phone", "phone app", "android", "smartphone"])

                    # Populate Mobile AI-integrated lists for JSON output
                    # AI-integrated by Keywords AND Mobile by Keywords
                    if is_ai_by_keywords and is_mobile_by_keywords:
                        ai_integrated_by_keywords_mobile_list.append({
                            "app_name": app_title,
                            "app_id": app_id,
                            "app_link": f"https://play.google.com/store/apps/details?id={app_id}",
                            "llm_keywords_detected": sorted(list(set(llm_indicator_in_description + list(consolidated_review_keywords))))
                        })

                    # AI-integrated by Cohere AND Mobile by Keywords
                    if is_ai_by_cohere and is_mobile_by_keywords:
                        ai_integrated_by_cohere_mobile_list.append({
                            "app_name": app_title,
                            "app_id": app_id,
                            "app_link": f"https://play.google.com/store/apps/details?id={app_id}",
                            "cohere_llm_type": cohere_llm_type
                        })

                else:
                    print(f"Skipping URL due to missing app title: {line}")
            else:
                print(f"Could not extract app ID from URL: {line}")

    # Save the full scraped data
    functions_with_description.save_as_json(all_apps_data, 'data/gp_data_safety_with_description_v4.json')
    print(f"\n{len(all_apps_data)} apps data saved to gp_data_safety_with_description_v4.json")

    # --- Save Overall AI-integrated apps to JSON ---
    keywords_overall_json_filename = f"data/ai_integrated_by_keywords_overall_{timestamp}.json"
    functions_with_description.save_as_json(ai_integrated_by_keywords_overall_list, keywords_overall_json_filename)
    print(f"Saved {len(ai_integrated_by_keywords_overall_list)} AI-integrated apps (by keywords, overall) to {keywords_overall_json_filename}")

    cohere_overall_json_filename = f"data/ai_integrated_by_cohere_overall_{timestamp}.json"
    functions_with_description.save_as_json(ai_integrated_by_cohere_overall_list, cohere_overall_json_filename)
    print(f"Saved {len(ai_integrated_by_cohere_overall_list)} AI-integrated apps (by Cohere, overall) to {cohere_overall_json_filename}")

    # --- Save Mobile AI-integrated apps to JSON ---
    keywords_mobile_json_filename = f"data/ai_integrated_by_keywords_mobile_{timestamp}.json"
    functions_with_description.save_as_json(ai_integrated_by_keywords_mobile_list, keywords_mobile_json_filename)
    print(f"Saved {len(ai_integrated_by_keywords_mobile_list)} AI-integrated and mobile apps (by keywords) to {keywords_mobile_json_filename}")

    cohere_mobile_json_filename = f"data/ai_integrated_by_cohere_mobile_{timestamp}.json"
    functions_with_description.save_as_json(ai_integrated_by_cohere_mobile_list, cohere_mobile_json_filename)
    print(f"Saved {len(ai_integrated_by_cohere_mobile_list)} AI-integrated and mobile apps (by Cohere) to {cohere_mobile_json_filename}")

    # --- Calculate Overlap for Mobile AI Apps ---
    keywords_mobile_app_ids = {app['app_id'] for app in ai_integrated_by_keywords_mobile_list}
    cohere_mobile_app_ids = {app['app_id'] for app in ai_integrated_by_cohere_mobile_list}

    overlap_mobile_app_ids = keywords_mobile_app_ids.intersection(cohere_mobile_app_ids)
    overlap_mobile_apps_count = len(overlap_mobile_app_ids)
    functions_with_description.save_as_json(list(overlap_mobile_app_ids), f"data/overlap_mobile_apps_{timestamp}.json")

    keywords_only_mobile_app_ids = keywords_mobile_app_ids - cohere_mobile_app_ids
    # keywords_only_mobile_apps_count = len(keywords_only_mobile_app_ids)

    cohere_only_mobile_app_ids = cohere_mobile_app_ids - keywords_mobile_app_ids
    # cohere_only_mobile_apps_count = len(cohere_only_mobile_app_ids)

    # --- Final Comparison Summary (Printed to TXT file AND Terminal) ---
    print("\n" + "=" * 60)
    print("                 FINAL ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Analysis run on: {datetime.datetime.now()}")
    print(f"Total apps processed: {total_apps_processed}")

    print("\n--- Overall AI-Integrated App Detection ---")
    print(f"Apps identified as AI-integrated by Keywords (overall): {len(ai_integrated_by_keywords_overall_list)}")
    print(f"Apps identified as AI-integrated by Cohere (overall): {len(ai_integrated_by_cohere_overall_list)}")

    print("\n--- Mobile-Based AI-Integrated App Detection (using Keyword-based Mobile Filter) ---")
    print(f"Apps identified as Mobile AI by Keywords (AI by Keywords + Mobile by Keywords): {len(ai_integrated_by_keywords_mobile_list)}")
    print(f"Apps identified as Mobile AI by Cohere (AI by Cohere + Mobile by Keywords): {len(ai_integrated_by_cohere_mobile_list)}")
    print(f"Overlap (Apps identified by BOTH keyword-AI/mobile and Cohere-AI/keyword-mobile methods): {overlap_mobile_apps_count}")
    # print(f"Apps identified as Mobile AI by Keywords ONLY: {keywords_only_mobile_apps_count}")
    # print(f"Apps identified as Mobile AI by Cohere ONLY: {cohere_only_mobile_apps_count}")
    print("=" * 60)

    # Close the log file and restore stdout
    log_file.close() # Close the file explicitly
    sys.stdout = original_stdout # Restore original stdout

    print(f"Analysis complete. Full output also saved to {output_filename}")


if __name__ == '__main__':
    main()