from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from langchain.llms import OpenAI  # Or LM Studio if needed

import re
import functions

# Initialize FastAPI
app = FastAPI()


# Define a Pydantic model for the incoming request
class CompareRequest(BaseModel):
    ppaf_file: str
    gp_file: str


# Use LM Studio setup, base_url can change according to what model is running by using port 5000 is best.
llm = OpenAI(base_url="http://127.0.0.1:5000/v1", api_key="not-needed", temperature=0)


def compare_llm(ppaf_data, gp_data):
    if not ppaf_data.strip() or not gp_data.strip(): #check if empty strings
        return "0"  # means they do not match

    prompt = f"""
       Given the following two pieces of text, provide a similarity score from 0 to 100 
       based on their meaning and context. A score of 0 means the texts are not similar at all, and a score of 100 means 
       they are exactly the same in meaning. Provide the score in the format, "score:".


       Text 1: {ppaf_data}
       Text 2: {gp_data}
       """
    try:
        response = llm(prompt)  # Send request to the local model using Langchain

        # Using regex to extract the first numeric value as the similarity score, this can be removed to collect the entire LM response.
        match = re.search(r': (\d+)', response)
        if match:
            return match.group(1)  # Return the score as a string (for consistency)
        else:
            return "0"

    except Exception as e:
        return {"error": str(e)}


def merge_sections(data):
    if isinstance(data, str):
        return data
    finalstring = ""
    for key, value in data.items():
        if isinstance(value, dict):
            finalstring += merge_sections(value)
        else:
            finalstring += merge_sections(value) + " "
    return finalstring.strip()


# FastAPI endpoint to handle comparison
@app.post("/compare")
async def compare_app_data(compare_request: CompareRequest):
    try:
        # Load JSON data
        ppaf_file = compare_request.ppaf_file
        gp_file = compare_request.gp_file

        with open(ppaf_file, 'r') as f1, open(gp_file, 'r') as f2:
            ppaf_data = json.load(f1)
            gp_data = json.load(f2)

        app_llm = {}  # to store LLM similarity results

        for app_id in ppaf_data:
            if app_id in gp_data:
                print(f"Finding similarities in {app_id}")
                ppaf_data_shared = ppaf_data[app_id].get('Data Shared', '')
                gp_data_shared = merge_sections(gp_data[app_id].get('Data shared', ''))

                ppaf_data_coll = ppaf_data[app_id].get('Data Collected', '')
                gp_data_coll = merge_sections(gp_data[app_id].get('Data collected', ''))

                ppaf_security = ppaf_data[app_id].get('Security Practices', '')
                gp_security = merge_sections(gp_data[app_id].get('Security practices', ''))

                # Compare data sections using LLM
                llm_sim = {'Data shared': compare_llm(ppaf_data_shared, gp_data_shared),
                           'Data collected': compare_llm(ppaf_data_coll, gp_data_coll),
                           'Security practices': compare_llm(ppaf_security, gp_security)
                           }

                app_llm[app_id] = llm_sim
            else:
                app_llm[app_id] = "Not yet in file."

        functions.save_as_json(app_llm, 'policy_llm_similarities.json')
        return {"similarity_results": app_llm}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the files: {str(e)}")


@app.get("/")  # default page
async def read_root():
    return {"message": "run 'uvicorn llm_analyze:app --reload' before running comparison program"}
