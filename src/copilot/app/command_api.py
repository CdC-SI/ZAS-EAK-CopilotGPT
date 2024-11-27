import logging
import re
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COMMANDS = {
    "/summarize": {"action": "load_summarize_prompt"},
    "/translate": {"action": "load_translate_prompt_OR_deepl_translate"},
    "/explain": {"action": "load_explain_prompt"},
    "/search": {"action": "load_search_prompt"},
    "/clear_memory": {"action": "clear_memory"},
    "/save_state": {"action": "save_state"},
    "/set_tone": {"action": "set_tone"},
    "/bookmark": {"action": "bookmark"},
    "/context": {"action": "context"},
    "/help": {"action": "display_help_info"},
}


class CommandRequest(BaseModel):
    input_text: str


@app.post("/")
async def command(request: CommandRequest):
    input_text = request.input_text.strip()
    response = {"command_recognized": False}

    for cmd, action in COMMANDS.items():
        if input_text.startswith(cmd):
            response["command_recognized"] = True
            response["command"] = cmd
            # response['action'] = action['action']
            break

    return JSONResponse(content=response)


@app.post("/advanced")
async def advanced_command(request: CommandRequest):
    input_text = request.input_text.strip()
    response = {"command_recognized": False}

    # Regular expression pattern for commands
    pattern = r"^/(\w+)(?:\s+(.*))?$"
    match = re.match(pattern, input_text)

    if match:
        cmd_name = f"/{match.group(1)}"
        parameters = match.group(2)  # Optional parameters
        if cmd_name in COMMANDS:
            response["command_recognized"] = True
            response["command"] = cmd_name
            # response['action'] = COMMANDS[cmd_name]['action']
            if parameters:
                response["parameters"] = parameters
    return JSONResponse(content=response)
