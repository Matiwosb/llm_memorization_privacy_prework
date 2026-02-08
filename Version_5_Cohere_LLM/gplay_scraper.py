import functions_with_description
import re # Import the re module for regular expressions
import json
import cohere
import time

# Initialize the Cohere client with your API key
cohere_client = cohere.Client("Your-Cohere-API-Key-Here")  # Replace with your actual Cohere API key

# Keywords to identify LLMs in app descriptions and reviews
description_and_review_llm_keywords =["AI-powered", "GPT", "ChatGPT", "Claude", "Gemini", "LLaMA", "Mistral","LLM", "language model",
                           "transformer model", "GPT-4", "GPT-3.5", "GPT-3", "DeepSeek V3", "DeepSeek R1", "GPT-4o",
                           "Gemini Pro 1.5", "Claude", "AI assistant", "AI chatbot", "AI writer", "AI-driven",
                           "AI-based", "AI-enhanced", "AI-enabled", "AI picture generator", "AI avatar maker",
                           "AI photo generator", "AI avatars", "AI art", "AI-Driven", "AI video", "Generative AI"]

def main():
    # if not os.path.exists('data'):
    #     os.makedirs('data')

    functions_with_description.collect_urls() # Uncomment if you need to re-collect URLs

    all_apps_data = {}

    # Counters for comparison of ALL AI apps (from previous step)
    llm_detected_by_keywords_overall = 0
    llm_detected_by_cohere_overall = 0

    # Counters for Mobile-Based AI-Integrated Apps (Step 2)
    mobile_ai_detected_by_keywords = 0
    mobile_ai_detected_by_cohere = 0
    mobile_ai_overlap = 0 # To count apps identified by BOTH methods

    total_apps_processed = 0 # Counter for total apps to ensure accuracy of percentages later

    with open('data/gs_urls_v5.txt', 'r') as file:
        for line in file:
            line = line.strip()
            app_id_match = re.search(r'id=([^&]+)', line)
            app_id = app_id_match.group(1) if app_id_match else None

            if app_id:
                total_apps_processed += 1 # Increment total apps processed

                data_safety, app_title = functions_with_description.scrape_data_safety(line)
                description = functions_with_description.get_app_description(app_id)

                # Cohere Classification for LLM type
                cohere_llm_type = functions_with_description.classify_llm_with_cohere(description, cohere_client)
                time.sleep(1)

                # Cohere Classification for Mobile Only
                cohere_only_mobile = functions_with_description.detect_mobile_only_with_cohere(description, cohere_client)
                time.sleep(1)

                # Analyze description for LLM-related keywords (Manual LLM Detection)
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

                    app_entry = {
                        "app_id": app_id,
                        "description": description,
                        "llm_indicator_in_description": llm_indicator_in_description,
                        "data_safety": data_safety,
                        "cohere_llm_type": cohere_llm_type,
                        "cohere_only_mobile": cohere_only_mobile,
                        "llm_indicator_in_review_summary": sorted(list(consolidated_review_keywords))
                    }
                    all_apps_data[app_title] = app_entry

                    # --- Overall AI Detection (Step 1 Validation) ---
                    # An app is considered AI-integrated by keywords if keywords are found in description OR review
                    is_ai_by_keywords = bool(llm_indicator_in_description) or bool(consolidated_review_keywords)
                    if is_ai_by_keywords:
                        llm_detected_by_keywords_overall += 1

                    # An app is considered AI-integrated by Cohere if Cohere identifies an LLM type
                    is_ai_by_cohere = (cohere_llm_type not in ["None", "No description", "Cohere failed"])
                    if is_ai_by_cohere:
                        llm_detected_by_cohere_overall += 1


                    # --- Mobile-Based AI-Integrated Apps (Step 2 Implementation) ---
                    description_lower = description.lower()
                    is_mobile_by_keywords = any(mobile_word in description_lower for mobile_word in ["mobile", "phone", "phone app", "android", "smartphone"])

                    # Check for mobile AI using Keywords + Keywords for AI
                    if is_mobile_by_keywords and is_ai_by_keywords:
                        mobile_ai_detected_by_keywords += 1

                    # Check for mobile AI using Cohere for Mobile + Cohere for AI
                    if cohere_only_mobile == "Yes" and is_ai_by_cohere:
                        mobile_ai_detected_by_cohere += 1

                    # Check for overlap
                    if (is_mobile_by_keywords and is_ai_by_keywords) and \
                       (cohere_only_mobile == "Yes" and is_ai_by_cohere):
                        mobile_ai_overlap += 1

                else:
                    print(f"Skipping URL due to missing app title: {line}")
            else:
                print(f"Could not extract app ID from URL: {line}")

    print("\nApp data collection complete.")
    functions_with_description.save_as_json(all_apps_data, 'data/gp_data_safety_with_description_v5.json')
    print(f"{len(all_apps_data)} apps data saved to gp_data_safety_with_description_v5.json")

    # ____________Filter for mobile apps and output summary and save to json file____________
    # This part can now primarily be for reporting, as the counting logic is integrated above
    mobile_apps_summary = []
    for app_title, app_info in all_apps_data.items():
        description = app_info.get("description", "").lower()
        cohere_llm_type = app_info.get("cohere_llm_type", "None.")
        cohere_only_mobile_status = app_info.get("cohere_only_mobile", "None.")
        app_id = app_info.get("app_id", None)

        is_mobile_by_keywords = any(mobile_word in description for mobile_word in ["mobile", "phone", "phone app", "android", "smartphone"])
        is_ai_by_keywords = bool(app_info.get("llm_indicator_in_description")) or bool(app_info.get("llm_indicator_in_review_summary"))
        is_ai_by_cohere = (cohere_llm_type not in ["None", "No description", "Cohere failed"])

        # Only add to summary if it's considered mobile AI by at least one method
        if (is_mobile_by_keywords and is_ai_by_keywords) or \
           (cohere_only_mobile_status == "Yes" and is_ai_by_cohere):

            app_link = f"https://play.google.com/store/apps/details?id={app_id}" if app_id else "N/A"

            mobile_apps_summary.append({
                "app_name": app_title,
                "app_link": app_link,
                "llm_types_detected_keywords": app_info.get("llm_indicator_in_description") + app_info.get("llm_indicator_in_review_summary"),
                "cohere_llm_type": cohere_llm_type,
                "cohere_only_mobile_detection": cohere_only_mobile_status,
                "is_mobile_ai_by_keywords": is_mobile_by_keywords and is_ai_by_keywords,
                "is_mobile_ai_by_cohere": cohere_only_mobile_status == "Yes" and is_ai_by_cohere
            })

    with open('data/mobile_apps_summary_v5.json', 'w') as summary_file:
        json.dump(mobile_apps_summary, summary_file, indent=4)

    print(f"Saved {len(mobile_apps_summary)} potentially mobile AI apps to data/mobile_apps_summary_v5.json")

    # --- Final Comparison Summary ---
    print("\n--- Final Comparison Summary ---")
    print(f"Total apps processed: {total_apps_processed}")
    print("\n--- Step 1: Overall AI-Integrated App Detection ---")
    print(f"Apps identified as AI-integrated by Keywords (description/reviews): {llm_detected_by_keywords_overall}")
    print(f"Apps identified as AI-integrated by Cohere (from description): {llm_detected_by_cohere_overall}")

    print("\n--- Step 2: Mobile-Based AI-Integrated App Detection ---")
    print(f"Apps identified as Mobile AI by Keywords (description keywords for mobile AND AI keywords): {mobile_ai_detected_by_keywords}")
    print(f"Apps identified as Mobile AI by Cohere (Cohere's mobile detection AND Cohere's AI detection): {mobile_ai_detected_by_cohere}")
    print(f"Apps identified as Mobile AI by BOTH Keyword and Cohere methods (Overlap): {mobile_ai_overlap}")

    # You can add more detailed comparisons here, e.g., apps identified by A but not B, vice-versa.
    # For example, to find apps identified by keywords but NOT by Cohere as Mobile AI:
    # Iterate through all_apps_data and check conditions
    keyword_only_mobile_ai_apps = []
    cohere_only_mobile_ai_apps = []
    for app_title, app_info in all_apps_data.items():
        description_lower = app_info.get("description", "").lower()
        is_mobile_by_keywords = any(mobile_word in description_lower for mobile_word in ["mobile", "phone", "phone app", "android", "smartphone"])
        is_ai_by_keywords = bool(app_info.get("llm_indicator_in_description")) or bool(app_info.get("llm_indicator_in_review_summary"))
        is_ai_by_cohere = (app_info.get("cohere_llm_type") not in ["None", "No description", "Cohere failed"])
        cohere_only_mobile_status = app_info.get("cohere_only_mobile")

        is_mobile_ai_by_keywords_combined = is_mobile_by_keywords and is_ai_by_keywords
        is_mobile_ai_by_cohere_combined = (cohere_only_mobile_status == "Yes" and is_ai_by_cohere)

        if is_mobile_ai_by_keywords_combined and not is_mobile_ai_by_cohere_combined:
            keyword_only_mobile_ai_apps.append(app_title)
        elif not is_mobile_ai_by_keywords_combined and is_mobile_ai_by_cohere_combined:
            cohere_only_mobile_ai_apps.append(app_title)

    print(f"\nApps identified as Mobile AI by Keywords ONLY: {len(keyword_only_mobile_ai_apps)}")
    # print(f"  Examples: {keyword_only_mobile_ai_apps[:5]}...") # Uncomment to see examples
    print(f"Apps identified as Mobile AI by Cohere ONLY: {len(cohere_only_mobile_ai_apps)}")
    # print(f"  Examples: {cohere_only_mobile_ai_apps[:5]}...") # Uncomment to see examples


if __name__ == '__main__':
    main()