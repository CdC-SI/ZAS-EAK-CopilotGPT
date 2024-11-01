import os
from dotenv import load_dotenv
import deepl

load_dotenv()

DEEPL_API_KEY = os.environ.get("DEEPL_API_KEY", None)

class TranslationService:
    def __init__(self):
        self.translator = deepl.Translator(DEEPL_API_KEY)

    async def translate(self, input_text: str, target_lang: str) -> str:

        translation = self.translator.translate_text(input_text, target_lang=target_lang.upper())

        return translation.text

translation_service = TranslationService()