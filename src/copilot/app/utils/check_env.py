import sys


def check_env_vars(config):

    # Documentation
    documentation = {
        "eak_copilot": "https://cdc-si.github.io/ZAS-EAK-CopilotGPT/",
        "openai_api": "https://platform.openai.com/docs/models",
    }

    # Check environment variables for autocomplete
    if config["autocomplete"]["enabled"]:
        if config["autocomplete"]["results"]["limit"] < 0:
            print(
                f'Invalid value for "autocomplete.results.limit" in config/config.yaml. Please read the documentation at {documentation["eak_copilot"]} for more information.'
            )
            sys.exit(1)
        if config["autocomplete"]["exact_match"]["limit"] < 0:
            print(
                f'Invalid value for "autocomplete.exact_match.limit" in config/config.yaml. Please read the documentation at {documentation["eak_copilot"]} for more information.'
            )
            sys.exit(1)
        if not config["autocomplete"]["fuzzy_match"]["threshold"] >= 1:
            print(
                f'Invalid value for "autocomplete.fuzzy_match.threshold" in config/config.yaml. Please read the documentation at {documentation["eak_copilot"]} for more information.'
            )
            sys.exit(1)
        if config["autocomplete"]["fuzzy_match"]["limit"] < 0:
            print(
                f'Invalid value for "autocomplete.fuzzy_match.limit" in config/config.yaml. Please read the documentation at {documentation["eak_copilot"]} for more information.'
            )
            sys.exit(1)
        if config["autocomplete"]["semantic_similarity_match"]["limit"] < 0:
            print(
                f'Invalid value for "autocomplete.semantic_similarity_match.limit" in config/config.yaml. Please read the documentation at {documentation["eak_copilot"]} for more information.'
            )
            sys.exit(1)

    # Check environment variables for rag
    if config["rag"]["enabled"]:
        if config["rag"]["retrieval"]["top_k"] <= 0:
            print(
                f'Invalid value for "rag.retrieval.top_k" in config/config.yaml. Please read the documentation at {documentation["eak_copilot"]} for more information. NOTE: Will be extended soon to more than 1 retrieved document.'
            )
            sys.exit(1)
        if not config["rag"]["llm"]["temperature"] >= 0:
            print(
                f'Invalid value for "rag.llm.model" in config/config.yaml. Please read the documentation at {documentation["openai_api"]} for more information.'
            )
            sys.exit(1)
        if not config["rag"]["llm"]["max_output_tokens"] >= 1:
            print(
                f'Invalid value for "rag.llm.max_output_tokens" in config/config.yaml. Please read the documentation at {documentation["openai_api"]} for more information.'
            )
            sys.exit(1)
        if not 0 <= config["rag"]["llm"]["top_p"] <= 1:
            print(
                f'Invalid value for "rag.llm.top_p" in config/config.yaml. Please read the documentation at {documentation["openai_api"]} for more information.'
            )
            sys.exit(1)
        if not isinstance(config["rag"]["llm"]["stream"], bool):
            print(
                f'Invalid value for "rag.llm.stream" in config/config.yaml. Please read the documentation at {documentation["openai_api"]} for more information.'
            )
            sys.exit(1)

    # Check environment variables for indexing
    if config["indexing"]["enabled"]:
        if not isinstance(config["indexing"]["dev_mode"], bool):
            print(
                'Invalid value for "indexing.dev_mode" in config/config.yaml. Please read the documentation at https://cdc-si.github.io/eak-copilot/ for more information.'
            )
            sys.exit(1)
        if not isinstance(config["indexing"]["faq"]["auto_index"], bool):
            print(
                'Invalid value for "indexing.faq.auto_index" in config/config.yaml. Please read the documentation at https://cdc-si.github.io/eak-copilot/ for more information.'
            )
            sys.exit(1)
        if not isinstance(config["indexing"]["rag"]["auto_index"], bool):
            print(
                'Invalid value for "indexing.rag.auto_index" in config/config.yaml. Please read the documentation at https://cdc-si.github.io/eak-copilot/ for more information.'
            )
            sys.exit(1)
