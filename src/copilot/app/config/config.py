import os

import yaml
from enum import Enum
from typing import Dict

from .autocomplete.config import AutocompleteConfig as AutocompleteParams
from .rag.config import RAGConfig as RAGParams
from config.indexing.config import IndexingConfig as IndexingParams


class Services(Enum):
    autocomplete = AutocompleteParams
    rag = RAGParams
    indexing = IndexingParams


def get_path(path: str) -> str:
    return os.path.join(os.path.dirname(__file__), path)


# Path to the YAML configuration file
CONFIG_PATH = get_path('config.yaml')
APP_CONFIG_PATH = get_path('app_config.yaml')


def load_config():
    with open(CONFIG_PATH, 'r') as file:
        config = yaml.safe_load(file)

    configs = {}
    for service in Services:
        params = config.get(service.name)
        params = params if isinstance(params, dict) else {'enabled': bool(params)}

        configs.update({service.name: service.value(**params)})

    return configs


def load_fastapi_config() -> dict:
    with open(APP_CONFIG_PATH, 'r') as file:
        app_config = yaml.safe_load(file)

    contact: Dict = app_config.get('contact')
    license_info: Dict = app_config.get('license_info')

    configs = {}
    for service in Services:
        config = app_config.get(service.name)
        config.update({'contact': contact, 'license_info': license_info})
        configs.update({service.name: config})

    return configs


Config = load_config()
AutocompleteConfig = Config.get(Services.autocomplete.name)
IndexingConfig = Config.get(Services.indexing.name)
RAGConfig = Config.get(Services.rag.name)

AppConfig = load_fastapi_config()
AutocompleteConfigApp = AppConfig.get(Services.autocomplete.name)
IndexingConfigApp = AppConfig.get(Services.indexing.name)
RAGConfigApp = AppConfig.get(Services.rag.name)
