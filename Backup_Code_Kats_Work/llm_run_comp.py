import requests

# Define the URL of the FastAPI server
url = "http://127.0.0.1:8000/compare"

# Define the data to send in the POST request
data = {
    "ppaf_file": "data/ppaf_data.json",
    "gp_file": "data/google_dss.json"
}

# Send the POST request with the data
response = requests.post(url, json=data)

# Print the response from the server
print(response.json())  # JSON response from the server
