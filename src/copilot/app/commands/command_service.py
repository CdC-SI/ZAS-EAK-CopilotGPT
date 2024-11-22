import os
from dotenv import load_dotenv
from typing import List, Tuple, Dict, Any
from collections.abc import Callable

from schemas.chat import ChatRequest
from rag.llm.base import BaseLLM
from utils.streaming import StreamingHandler
from chat.memory import ConversationalMemory

import deepl

from langfuse.decorators import observe

load_dotenv()

DEEPL_API_KEY = os.environ.get("DEEPL_API_KEY", None)

class TranslationService:
    def __init__(self):
        self.translator = deepl.Translator(DEEPL_API_KEY)

    async def translate(self, input_text: str, target_lang: str) -> str:

        translation = self.translator.translate_text(input_text, target_lang=target_lang.upper())

        return translation.text

class CommandService:
    def __init__(self, translation_service, message_builder):
        self.translation_service = translation_service
        self.message_builder = message_builder

    def parse_args(self, command_args: str) -> List[str]:
        return command_args.split()

    def get_summarize_args(self, args: List[str]) -> Tuple[str, int, str]:
        summary_mode = (
            args[0]
            if len(args) > 0 and args[0] in ["last", "all", "highlights"]
            else "all"
        )

        n_msg = -1
        if summary_mode == "last" and len(args) > 1 and args[1].isdigit():
            n_msg = int(args[1])

        # Determine summary style (default to "concise" if not specified or invalid)
        summary_style = (
            args[-1]
            if len(args) > 1
            and args[-1] in ["formal", "concise", "detailed", "bulletpoint"]
            else "concise"
        )

        return summary_mode, n_msg, summary_style

    def get_translate_args(self, args: List[str]) -> Tuple[int, str]:
        translate_mode = args[0] if len(args) > 0 and args[0] in ["last", "all"] else "all"

        n_msg = -1
        if translate_mode == "last" and len(args) > 1 and args[1].isdigit():
            n_msg = int(args[1])

        target_lang = (
            args[-1]
            if len(args) > 1 and args[-1] in ["ar", "bg", "cs", "da", "de", "el", "en-gb", "en-us", "es", "et", "fi", "fr", "hu", "id", "it", "ja", "ko", "lv", "nb", "nl", "pl", "pt-br", "pt-pt", "ro", "ru", "sk", "sl", "sv", "tr", "uk", "zh-hans", "zh-hant"] else "de"
        )

        return n_msg, target_lang

    def map_summary_style_to_language(self, language: str, style: str) -> str:
        mapping = {
            "de": {
                "formal": "formell",
                "concise": "knapp",
                "detailed": "detailliert",
                "bulletpoint": "bulletpoint",
            },
            "fr": {
                "formal": "formel",
                "concise": "concis",
                "detailed": "détaillé",
                "bulletpoint": "bulletpoint",
            },
            "it": {
                "formal": "formale",
                "concise": "conciso",
                "detailed": "dettagliato",
                "bulletpoint": "bulletpoint",
            },
        }

        return mapping[language][style].upper()

    def map_summary_mode_to_language(self, language: str, mode: str) -> str:
        mapping = {
            "de": {
                "last": "den gesamten",  # already retrieved last n_msg
                "all": "den gesamten",
                "highlights": "die wichtigsten Fakten (Highlights)",
            },
            "fr": {
                "last": "l'ensemble",  # already retrieved last n_msg
                "all": "l'ensemble",
                "highlights": "les faits marquants (highlights)",
            },
            "it": {
                "last": "sull'intero",  # already retrieved last n_msg
                "all": "sull'intero",
                "highlights": "sui fatti chiave (highlights)",
            },
        }

        return mapping[language][mode].upper()

    async def translate(self, input_text: str, target_lang: str) -> str:
        return await self.translation_service.translate(input_text, target_lang)

    async def execute_command(self, request: ChatRequest, memory_client: ConversationalMemory) -> Dict[str, Any]:
        args = self.parse_args(request.command_args)
        if request.command == "/summarize":
            summary_mode, n_msg, summary_style = self.get_summarize_args(args)
            input_text = ""
            if request.user_uuid:
                input_text = memory_client.memory_instance.format_conversational_memory(
                    request.user_uuid, request.conversation_uuid, n_msg
                )
            summary_style = self.map_summary_style_to_language(request.language, summary_style)
            summary_mode = self.map_summary_mode_to_language(request.language, summary_mode)
            messages = self.message_builder.build_summarize_prompt(
                request.command, input_text, mode=summary_mode, style=summary_style
            )
            return {"messages": messages}
        elif request.command == "/translate":
            n_msg, target_lang = self.get_translate_args(args)
            input_text = ""
            if request.user_uuid:
                input_text = memory_client.memory_instance.format_conversational_memory(
                    request.user_uuid, request.conversation_uuid, n_msg
                )
            translated_text = await self.translate(input_text, target_lang)
            return {"translated_text": translated_text}
        else:
            raise ValueError(f"Unknown command: {request.command}")

    @observe()
    async def process_command(self, request: ChatRequest, llm_client: BaseLLM, streaming_handler: StreamingHandler, memory_client: ConversationalMemory, sources: Dict):

        result = await self.execute_command(request, memory_client)
        messages = result.get("messages")
        translated_text = result.get("translated_text")

        # stream response
        if messages:
            event_stream = llm_client.call(messages)
            async for token in streaming_handler.generate_stream(event_stream, sources["source_url"]):
                yield token

        elif translated_text:
            for token in translated_text:
                yield token.encode("utf-8")
