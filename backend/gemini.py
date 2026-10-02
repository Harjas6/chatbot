import json
import os

from arxiv_search import search_arxiv
from chat_config import ARXIV, MAX_TOOL_CALLS, NEWS, SYSTEM_INSTRUCTION, TOOLS, WEB
from ddgs_search import search_news, search_web
from dotenv import load_dotenv
from google import genai
from models import ChatReply

load_dotenv()
model = os.environ["MODEL"]
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


LIMIT_NOTE = """Tool limit reached. Do not call any more tools. Using only the results
    you already have, write your final reply in the required format. If the
    results were empty or irrelevant, say so instead of guessing. 
    Tell the user this is why you could not get all the info they needed"""


COMMON = {
    "model": model,
    "tools": TOOLS,
    "system_instruction": SYSTEM_INSTRUCTION,
    "response_format": {
        "type": "text",
        "mime_type": "application/json",
        "schema": ChatReply.model_json_schema(),
    },
}
COMMON_NO_TOOLS = {
    "model": model,
    "system_instruction": SYSTEM_INSTRUCTION,
    "response_format": {
        "type": "text",
        "mime_type": "application/json",
        "schema": ChatReply.model_json_schema(),
    },
}


def get_function_call(interaction):
    for step in interaction.steps:
        if step.type == "function_call":
            return step

    return None


def handle_function_call(function_call):
    try:
        if function_call.name == ARXIV:
            return search_arxiv(**function_call.arguments)

        elif function_call.name == NEWS:
            return search_news(**function_call.arguments)

        elif function_call.name == WEB:
            return search_web(**function_call.arguments)

        else:
            return {"error": f"Unknown function call: {function_call.name}"}

    except Exception as e:
        return {"error": f"Failed to execute {function_call.name}: {e!s}"}


def ask_gemini(prompt: str, previous_transaction_id: str | None = None):

    # user input to gemini, with previous transaction id if available
    interaction = client.interactions.create(
        input=prompt, previous_interaction_id=previous_transaction_id, **COMMON
    )

    # check if gemini called a function, and handle it if so
    rounds = 0
    while (function_call := get_function_call(interaction)) is not None:
        rounds += 1
        result = handle_function_call(function_call)
        limit_reached = rounds >= MAX_TOOL_CALLS
        if limit_reached:
            payload = {"result": result, "note": LIMIT_NOTE}
        else:
            payload = result

        interaction = client.interactions.create(
            input=[
                {
                    "type": "function_result",
                    "name": function_call.name,
                    "call_id": function_call.id,
                    "result": [{"type": "text", "text": json.dumps(payload)}],
                }
            ],
            previous_interaction_id=interaction.id,
            **(COMMON_NO_TOOLS if limit_reached else COMMON),
        )
        if limit_reached:
            break

    try:
        reply = ChatReply.model_validate_json(interaction.output_text)
    except Exception:
        reply = ChatReply(
            response=f"I wasn't able to fully answer your question. Your request required "
            f"more than {MAX_TOOL_CALLS} searches (arXiv/live search lookups) to address properly. "
            f"Try asking about fewer topics or papers at once.",
            justification=f"The tool limit was reached after {MAX_TOOL_CALLS} tool calls,"
            " and the structured response could not be generated.",
            sources=[],
        )
    reply.transaction_id = interaction.id
    return reply
