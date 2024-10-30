import requests

user_uuid = "04001f7b-224b-47ae-8fdf-9e9135255cdG"
conversation_uuid = "a90a6103-2092-4e08-8cb9-bea9396ec420"

# Test the GET /apy/conversations endpoint
url = "http://localhost:8000/apy/conversations"

params = {
    "user_uuid": user_uuid
}

response = requests.get(url, params=params)

print("TESTING: http://localhost:8000/apy/conversations")
print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(response.json())
print("--------------------------------")

# Test the GET /apy/conversations/{conversation_uuid} endpoint

# Define the parameters
url = f"http://localhost:8000/apy/conversations/{conversation_uuid}"

# Make a GET request to the endpoint
response = requests.get(url)

# Print the response status code and JSON content
print("TESTING: http://localhost:8000/apy/conversations/{conversation_uuid}")
print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(response.json())
print("--------------------------------")

# Test the GET /apy/conversations/titles endpoint
url = "http://localhost:8000/apy/conversations/titles"

# Define the parameters
params = {
    "user_uuid": user_uuid
}

# Make a GET request to the endpoint
response = requests.get(url, params=params)

# Print the response status code and JSON content
print("TESTING: http://localhost:8000/apy/conversations/titles")
print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(response.json())
print("--------------------------------")

# Test the PUT /apy/conversations/feedback/thumbs_up endpoint
message_uuid = "545f2e29-4d87-488f-b3fe-47cc699b6d13"

# url = "http://localhost:8000/apy/conversations/feedback/thumbs_up"
# params = {
#     "user_uuid": user_uuid,
#     "conversation_uuid": conversation_uuid,
#     "message_uuid": message_uuid
# }

# # Make the PUT request
# response = requests.put(url, params=params)

# print("TESTING: http://localhost:8000/apy/conversations/feedback/thumbs_up")
# print(f"Status Code: {response.status_code}")
# print("Response JSON:")
# print(response.json())
# print("--------------------------------")

# Test the PUT /apy/conversations/feedback/thumbs_down endpoint
url = "http://localhost:8000/apy/conversations/feedback/thumbs_down"
params = {
    "user_uuid": user_uuid,
    "conversation_uuid": conversation_uuid,
    "message_uuid": message_uuid,
    "comment": "SUPER BAD!!!"
}

# Make the PUT request
response = requests.put(url, params=params)

print("TESTING: http://localhost:8000/apy/conversations/feedback/thumbs_down")
print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(response.json())
print("--------------------------------")
