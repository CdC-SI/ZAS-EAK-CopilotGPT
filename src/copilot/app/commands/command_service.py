from typing import List, Tuple

class CommandService:

    def __init__(self):
        pass

    def execute_command(self, command: str, command_args: str, input_text: str):
        args = self.parse_args(command_args)
        if command == "/summarize":
            return self.summarize(*args, input_text)
        elif command == "/translate":
            return self.translate()
        elif command == "/explain":
            return self.explain(command_args, input_text)

    def parse_args(self, command_args: str) -> List[str]:
        args = command_args.split()
        return args

    def get_summarize_args(self, args: List[str]) -> Tuple[str, int, str]:
        summary_mode = args[0] if len(args) > 0 and args[0] in ["last", "all", "highlights"] else "all"

        n_msg = -1
        if summary_mode == "last" and len(args) > 1 and args[1].isdigit():
            n_msg = int(args[1])

        # Determine summary style (default to "concise" if not specified or invalid)
        summary_style = args[-1] if len(args) > 1 and args[-1] in ["formal", "concise", "detailed", "bulletpoint"] else "concise"

        return summary_mode, n_msg, summary_style

    def map_style_to_language(self, language: str, style: str) -> str:
        mapping = {
            "de": {
                "formal": "formell",
                "concise": "knapp",
                "detailed": "detailliert",
                "bulletpoint": "bulletpoint"
                },
            "fr": {
                "formal": "formel",
                "concise": "concis",
                "detailed": "détaillé",
                "bulletpoint": "bulletpoint"
                },
            "it": {
                "formal": "formale",
                "concise": "conciso",
                "detailed": "dettagliato",
                "bulletpoint": "bulletpoint"
                },
            }

        return mapping[language][style].upper()

    def map_mode_to_language(self, language: str, mode: str) -> str:
        mapping = {
            "de": {
                "last": "den gesamten", # already retrieved last n_msg
                "all": "den gesamten",
                "highlights": "die wichtigsten Fakten (highlights)",
                },
            "fr": {
                "last": "l'ensemble", # already retrieved last n_msg
                "all": "l'ensemble",
                "highlights": "les faits marquants (highlights)",
                },
            "it": {
                "last": "sull'intero", # already retrieved last n_msg
                "all": "sull'intero",
                "highlights": "sui fatti chiave (highlights)",
                },
            }

        return mapping[language][mode].upper()

    def summarize(self, *args, input_text):
        pass

    def translate(self):
        pass

    def explain(self, command_args: str, input_text: str):
        pass

command_service = CommandService()
