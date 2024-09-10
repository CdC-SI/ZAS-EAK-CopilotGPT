import os

import yaml
from enum import Enum
from typing import Dict, ItemsView
from dataclasses import asdict, is_dataclass

from .autocomplete.config import AutocompleteConfig as AutocompleteParams
from .rag.config import RAGConfig as RAGParams
from config.indexing.config import IndexingConfig as IndexingParams

from utils.logging import get_logger
logger = get_logger(__name__)


class Services(Enum):
    autocomplete = AutocompleteParams
    rag = RAGParams
    indexing = IndexingParams


def get_path(path: str) -> str:
    return os.path.join(os.path.dirname(__file__), path)


# Path to the YAML configuration file
CONFIG_PATH = get_path('config.yaml')
RUNNING_CONFIG_PATH = get_path('config_running.yaml')
APP_CONFIG_PATH = get_path('config_app.yaml')


def enum_handling_dict(data):
    """
    Used in the dataclasses.asdict() method to handle Enum values, as the dict_factory parameter.
    """
    d = {}
    for k, v in data:
        if isinstance(v, Enum):
            if is_dataclass(v.value):
                d.update({k: enum_handling_dict(asdict(v.value).items())})
            else:
                d.update({k: v.name})
        else:
            d.update({k: v})
            if k == 'enabled' and not v:
                return d
    return d


def load_config():
    """
    Load the app configuration from config.yaml file to dataclasses then save the running config in config.running.yaml.

    Returns
    -------
    dict
        A dictionary of service names and their respective configuration dataclasses.
    """
    with open(CONFIG_PATH, 'r') as file:
        config = yaml.safe_load(file)
        config = config if isinstance(config, dict) else {}

    configs = {}
    for service in Services:
        params = config.get(service.name)
        if params is None:
            params = {}  # Default values
        elif not isinstance(params, dict):
            params = {'enabled': bool(params)}

        configs.update({service.name: service.value(**params)})

    with open(RUNNING_CONFIG_PATH, 'w+') as file:
        yaml.dump({key: asdict(value, dict_factory=enum_handling_dict) for key, value in configs.items()},
                  file,
                  allow_unicode=True)

    return configs


def load_fastapi_config() -> dict:
    """
    Load the FastAPI Swagger interface configuration from config_app.yaml file.

    Returns
    -------
    dict
        A dictionary of service names and their respective configuration dataclasses
    """
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
"""
A dictionary of service names and their respective configuration dataclasses to run the copilot."""

AutocompleteConfig = Config.get(Services.autocomplete.name)
"""
The configuration dataclass for the autocomplete service."""

IndexingConfig = Config.get(Services.indexing.name)
""""
The configuration dataclass for the indexing service."""

RAGConfig = Config.get(Services.rag.name)
"""
The configuration dataclass for the RAG service."""

EmbeddingConfig = Config.get('embedding')
"""
The configuration dataclass for the embedding model."""


AppConfig = load_fastapi_config()
"""
A dictionary of service names and their respective configuration dataclasses for the FastAPI Swagger app."""

AutocompleteConfigApp = AppConfig.get(Services.autocomplete.name)
"""
The configuration dataclass for the autocomplete service in the FastAPI Swagger app."""

IndexingConfigApp = AppConfig.get(Services.indexing.name)
"""
The configuration dataclass for the indexing service in the FastAPI Swagger app."""

RAGConfigApp = AppConfig.get(Services.rag.name)
"""
The configuration dataclass for the RAG service in the FastAPI Swagger app."""