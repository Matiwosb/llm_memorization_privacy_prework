# semantic_filter_cohere.py

import json
import cohere
import time

COHERE_API_KEY = ""  # <- Replace with your real API key!

# Load the apps from keyword search
with open('data/gp_data_safety_with_description_v4.json', 'r', encoding='utf-8') as f:
    apps = json.load(f)

co = cohere.Client(COHERE_API_KEY)

def is_ai_app_via_cohere(description: str) -> bool:
    prompt = (
        "Question: Does the following Google Play app integrate an AI large-language model (LLM) or intelligent automation? "
        "Answer 'Yes' or 'No'.\n\n"
        f"App description:\n{description}\n\nAnswer:"
    )
    try:
        response = co.generate(
            model='command',
            prompt=prompt,
            max_tokens=3,
            temperature=0.0,
            stop_sequences=["\n"]
        )
        answer = response.generations[0].text.strip().lower()
        return answer.startswith('yes')
    except Exception as e:
        print("Cohere error:", e)
        return False

ai_apps = []
for i, app in enumerate(apps):
    # PATCH: If app is a dict, use its fields. If string, just use it as desc.
    if isinstance(app, dict):
        desc = app.get('description', '')
        app_title = app.get('title', 'Unknown')
    elif isinstance(app, str):
        desc = app
        app_title = 'Unknown'
    else:
        desc = ''
        app_title = 'Unknown'
    
    if not desc.strip():
        continue
    print(f"Processing {i+1}/{len(apps)}: {app_title} ...", end=' ')
    if is_ai_app_via_cohere(desc):
        print("AI: YES")
        ai_apps.append(app)
    else:
        print("AI: NO")
    time.sleep(1.2) 

print(f"\n[Cohere filter] {len(ai_apps)} out of {len(apps)} apps marked as AI-integrated.")
with open('apps_cohere.json', 'w', encoding='utf-8') as f:
    json.dump(ai_apps, f, ensure_ascii=False, indent=2)
print("Saved filtered apps to apps_cohere.json")
