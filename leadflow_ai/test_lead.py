import requests

# Define the mock lead data
mock_lead = {
    "name": "Alice",
    "domain": "wellnessco.com",
    "zip": "12345",
    "interests": ["health", "wellness"]
}

# Define the API endpoint
url = "http://127.0.0.1:8000/ingest-lead"

# Send a POST request to the API endpoint
response = requests.post(url, json=mock_lead)

# Print the response from the server
if response.status_code == 200:
    data = response.json()
    print("Personalized Message:", data["message"])
    print("Matched Business:", data["matched_business"])
else:
    print("Failed to ingest lead. Status code:", response.status_code) 