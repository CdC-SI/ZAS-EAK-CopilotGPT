import requests

# Test the GET /apy/search/sources endpoint
url = "http://localhost:8000/apy/search/sources"

response = requests.get(url)

print("TESTING: http://localhost:8000/apy/search/sources")
print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(response.json())
print("--------------------------------")

# Test the GET /apy/search/tags endpoint
url = "http://localhost:8000/apy/search/tags"

response = requests.get(url)

print("TESTING: http://localhost:8000/apy/search/tags")
print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(response.json())
print("--------------------------------")

# Test the GET /apy/search/llm_models endpoint
url = "http://localhost:8000/apy/search/llm_models"

response = requests.get(url)

print("TESTING: http://localhost:8000/apy/search/llm_models")
print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(response.json())
print("--------------------------------")

# Test the GET /apy/search/retrieval_methods endpoint
url = "http://localhost:8000/apy/search/retrieval_methods"

response = requests.get(url)

print("TESTING: http://localhost:8000/apy/search/retrieval_methods")
print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(response.json())
print("--------------------------------")
