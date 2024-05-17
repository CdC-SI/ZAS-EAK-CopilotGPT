import os
from dotenv import load_dotenv
import yaml

# Load environment variables from .env file
load_dotenv()

# Path to the YAML configuration file
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')

# Load the YAML configuration file
with open(CONFIG_PATH, 'r') as file:
    config = yaml.safe_load(file)

# Access configuration values
autocomplete_config = config.get('autocomplete')
rag_config = config.get('rag')
indexing_config = config.get('indexing')
