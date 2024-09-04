import os

import yaml
from enum import Enum
from typing import Dict
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
RUNNING_CONFIG_PATH = get_path('running_config.yaml')
APP_CONFIG_PATH = get_path('app_config.yaml')


def enum_handling_dict(data):
    d = {}
    for k, v in data:
        logger.info(f'key: {k}, value: {v}')
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
    with open(CONFIG_PATH, 'r') as file:
        config = yaml.safe_load(file)
        config = config if isinstance(config, dict) else {}

    configs = {}
    for service in Services:
        params = config.get(service.name)
        if not isinstance(params, dict):
            params = {'enabled': bool(params)} if params is not None else {}

        configs.update({service.name: service.value(**params)})

    with open(RUNNING_CONFIG_PATH, 'w+') as file:
        yaml.dump({key: asdict(value, dict_factory=enum_handling_dict) for key, value in configs.items()},
                  file,
                  allow_unicode=True)

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
