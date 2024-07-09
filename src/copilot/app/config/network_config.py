import os
from dotenv import load_dotenv

import requests
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

# Load environment variables from .env file
load_dotenv()

# Load CORS config
CORS_ALLOWED_ORIGINS = os.environ["CORS_ALLOWED_ORIGINS"]

# override the methods which you use
requests.post = lambda url, **kwargs: requests.request(
    method="POST", url=url, verify=False, **kwargs
)

requests.get = lambda url, **kwargs: requests.request(
    method="GET", url=url, verify=False, **kwargs
)

disable_warnings(category=InsecureRequestWarning)
