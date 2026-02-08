import json
import cohere
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity

# ---------- CONFIG ----------
COHERE_API_KEY = "kSJ18cvLScuylf7o8SGFcwi5ycPIetzKjx8sEeLP"  # Replace this with your actual key
INPUT_FILE = "data/gp_data_safety_with_description_v4.json"  # Full scraped app list
OUTPUT_FILE = "data/cohere_scraped_apps.json"
SIM_THRESHOLD = 0.55
AI_PHRASES = [
    "AI chatbot", "powered by GPT", "uses artificial intelligence",
    "large language model", "LLM integration", "GPT-4", "machine learning model"
]
MOBILE_KEYWORDS = ["mobile", "android", "smartphone", "on your phone"]
os.makedirs("data", exist_ok=True)
# ---------------------------

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

def get_embedding(text):
    try:
        response = co.embed(
            texts=[text],
            model="embed-english-v3.0",
            input_type="search_document"
        )
        return response.embeddings[0]
    except Exception as e:
        print(f"[Cohere Error] {e}")
        return None

def is_ai_integrated(description, target_embeddings):
    if not description:
        return "None", 0.0
    emb = get_embedding(description)
    if emb is None:
        return "None", 0.0
    sims = cosine_similarity([emb], target_embeddings)[0]
    max_sim = float(max(sims))
    if max_sim >= SIM_THRESHOLD:
        return "AI-integrated (semantic)", max_sim
    return "None", max_sim

def is_mobile_app(description):
    desc = description.lower()
    return any(k in desc for k in MOBILE_KEYWORDS)

def main():
    # Load full scraped app list
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # If dictionary of dicts, convert to list of dicts
    if isinstance(raw_data, dict):
        all_apps = []
        for title, details in raw_data.items():
            if isinstance(details, dict):
                details['title'] = title
                all_apps.append(details)
    else:
        all_apps = raw_data

    print(f"Loaded {len(all_apps)} total apps")

    # Precompute target phrase embeddings
    # target_embeddings = [get_embedding(p) for p in AI_PHRASES if get_embedding(p)]
    target_embeddings = []
    for phrase in AI_PHRASES:
        emb = get_embedding(phrase)
        if emb:
            target_embeddings.append(emb)

    if not target_embeddings:
        print("Failed to embed target phrases. Exiting.")
        return

    cohere_matched_apps = []

    for app in all_apps:
        desc = app.get("description", "")
        app["cohere_llm_type"], app["cohere_score"] = is_ai_integrated(desc, target_embeddings)
        app["cohere_only_mobile"] = "Yes" if is_mobile_app(desc) else "No"

        if app["cohere_llm_type"] == "AI-integrated (semantic)":
            cohere_matched_apps.append(app)

    # Save filtered results
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(cohere_matched_apps, f, indent=2)

    print(f"✅ Saved {len(cohere_matched_apps)} AI-integrated apps to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
