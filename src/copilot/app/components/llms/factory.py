from components.llms.base import LLM
from components.llms.implementations import *

class LLMFactory:
    @staticmethod
    def get_llm_client(llm_model: str) -> LLM:
        """
        Factory method to instantiate llm clients based on a string identifier.

        Parameters
        ----------
        llm_model : str
            The name of the LLM model. Currently supported models are "gpt-3.5-turbo-0125", "gpt-4-turbo-preview", "gpt-4o", "mlx-community/Nous-Hermes-2-Mistral-7B-DPO-4bit-MLX" and "Qwen/Qwen1.5-0.5B-Chat-GGUF".

        Returns
        -------
        LLM
            An instance of the appropriate llm client.

        Raises
        ------
        ValueError
            If the `llm_model` is not supported.
        """
        if llm_model in ["gpt-3.5-turbo-0125", "gpt-4-turbo-preview", "gpt-4o"]:
            return OpenAILLM(model_name=llm_model)
        elif llm_model == "mlx-community/Nous-Hermes-2-Mistral-7B-DPO-4bit-MLX":
            return MistralLLM()
        elif llm_model == "Qwen/Qwen1.5-0.5B-Chat-GGUF":
            return QwenLLM()
        else:
            raise ValueError(f"Unsupported embedding model type: {llm_model}")
