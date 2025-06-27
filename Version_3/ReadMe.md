
# Google Play Store LLM App Analyzer

This project scrapes app information from the **Google Play Store**, including descriptions, reviews, and data safety pages, and analyzes them for mentions of **Large Language Models (LLMs)** like ChatGPT, GPT, Claude, Gemini or AI powered. It uses:

- `google-play-scraper` for structured app data
- `BeautifulSoup` for HTML parsing
- `Cohere` LLM API for intelligent text classification
- Keyword matching for LLM detection
- JSON export for downstream analysis

---

## Features

- ✅ Scrape app URLs based on keyword queries
- ✅ Collect app descriptions, reviews, and data safety details
- ✅ Detect LLM-related mentions using keyword search
- ✅ Use Cohere LLM to classify app descriptions intelligently
- ✅ Filter and export only mobile-focused LLM apps
- ✅ Save output to structured JSON files

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Matiwosb/llm_memorization_privacy_prework.git
cd llm_memorization_privacy_prework
```

### 2. Create a Python Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```
---

## API Key Setup

This project uses the [Cohere API](https://dashboard.cohere.com) to analyze app descriptions. Create a free Cohere account and:

1. Generate an API key
2. Set it in your script:

```python
import cohere
co = cohere.Client("your-api-key-here")
```

---

## Usage

### To scrape and analyze apps:

Run the main script:

```bash
python mobile_googleplay_scraper.py
```

This will:

- Collect Google Play app URLs
- Scrape descriptions, reviews, and data safety info
- Analyze for LLM-related content using keywords and Cohere
- Save two output files:
  - `data/gp_data_safety_with_description_vX.json` – full dataset
  - `data/mobile_apps_summary_vX.json` – filtered mobile apps with LLMs

---

## Project Structure

```
├── data/
│   ├── app_urls_vX.txt
│   ├── gs_urls_vX.txt
│   ├── gp_data_safety_with_description_vX.json
│   └── mobile_apps_summary_vX.json
├── functions_with_description.py
├── mobile_googleplay_scraper.py
└── README.md
```

---

## LLM Detection Methods

- **Keyword-based:** simple matching of known LLM-related terms like `"GPT"`, `"ChatGPT"`, `"Claude"`, etc.
- **Cohere-powered:** natural language classification of whether the app uses an LLM and which type.

---

## Output Example
`gp_data_safety_with_description_vX.json`
```json
{
    "Ask AI - Chat with AI Chatbot": {
        "app_id": "com.codeway.chatapp",
        "description": "Welcome to Ask AI \u2013 Discover Endless Possibilities Every Day!\r\n\r\nExperience conversations with an AI that understands you, adapts to your mood, and personalizes interactions, making each engagement unique....",
        "llm_indicator_in_description": [
            "AI chatbot",
        ],
        "data_safety": {
            "No data shared with third parties": {},
            "Data collected": {
                "App info and performance": "Crash logs, Diagnostics, and Other app performance data",
                "App activity": "App interactions and Other user-generated content",
                "Device or other IDs": "Device or other IDs",
                "Location": "Approximate location"
            },
            "Security practices": {
                "Data is encrypted in transit": "Your data is transferred over a secure connection",
                "Data can\u2019t be deleted": "The developer doesn\u2019t provide a way for you to request that your data be deleted"
            }
        },
        "cohere_llm_type": "GPT-4o.",
        "cohere_only_mobile": "No.",
        "llm_indicator_in_review_summary": [
            "ChatGPT",
            "Gemini"
        ]
    }
}
```

`mobile_apps_summary_vX.json`

```json
{
  "app_name": "Ask AI - Chat with AI Chatbot",
  "app_link": "https://play.google.com/store/apps/details?id=com.codeway.chatapp",
  "llm_types_detected": ["ChatGPT", "GPT"],
  "cohere_llm_type": "ChatGPT"
}
```

---

## Limitations

- The free Cohere API has a rate limit of **10 calls/minute** – script includes throttling.
- App scraping is limited to publicly available app data.

---

## License

MIT License. See `LICENSE` file for more information.

---
