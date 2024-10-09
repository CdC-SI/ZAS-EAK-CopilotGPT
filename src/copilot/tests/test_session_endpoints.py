import requests

# Test the GET /apy/session/get_chat_titles endpoint
url = "http://localhost:8000/apy/session/get_chat_titles"

params = {
    "user_uuid": "04001f7b-224b-47ae-8fdf-9e9135255cdB"
}

response = requests.get(url, params=params)

print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(response.json())

# Test the GET /apy/session/get_chat_history endpoint
url = "http://localhost:8000/apy/session/get_chat_history"

# Define the parameters
params = {
    "conversation_uuid": "a90a6103-2092-4e08-8cb9-bea9396ec499"
}

# Make a GET request to the endpoint
response = requests.get(url, params=params)

# Print the response status code and JSON content
print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(response.json())