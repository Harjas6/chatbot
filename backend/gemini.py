import json
import os

from dotenv import load_dotenv
from google import genai
from models import ChatReply
from my_arxiv import search_arxiv

load_dotenv()

SYSTEM_INSTRUCTION = """You are a conversational assistant that discusses two topics: ongoing AI news and generative AI research papers on arXiv.

Tools:
- Use the search_arxiv tool when the user asks about papers, research, or techniques from arXiv. Write a focused query, and use at most one search per message unless the first returns nothing.
- If the user asks about current AI news and you have no news tool available, say that news isn't available yet and offer to discuss arXiv papers instead. Do not answer news questions from memory as if they were current.

Conversation:
- Be conversational and natural. Use the earlier turns of the conversation to interpret follow-up questions (for example "tell me more about the second one").
- You only have each paper's title, authors, date, and abstract. When discussing a paper, base your answers on those. If the user asks for details that the abstract doesn't cover, say you only have the abstract and point them to the paper's link.
- If a request is outside AI news or genAI papers, politely steer back to those topics.

Every reply must have three parts:
1. response: the answer to the user's message, taking previous turns into account.
2. justification: a short explanation of why this response is appropriate, including whether you used a search and why.
3. sources: a list of links you actually used.

Rules for sources:
- Only include links that appeared in tool results. Never invent or guess URLs.
- If you did not use any sources (for example a greeting or a follow-up answered from earlier context), return an empty list.
- If a search returns nothing relevant, say so in the response instead of guessing."""
model = os.environ["MODEL"]
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

search_arxiv_tool = {
    "type": "function",
    "name": "search_arxiv",
    "description": "Searches arXiv for recent research papers. Use whenever the "
    "user asks about papers, research, or recent work on a topic. Build the "
    "query with arXiv syntax: field prefixes (ti:, abs:, au:, cat:) and "
    "AND/OR, e.g. 'cat:cs.CL AND abs:reasoning'. For generative AI topics, "
    "prefer categories cs.CL, cs.LG, cs.AI.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The arXiv search query string.",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of papers to return. Defaults to 5.",
            },
        },
        "required": ["query"],
    },
}
tools = [search_arxiv_tool]

COMMON = {
    "model": model,
    "tools": tools,
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
    if function_call.name == "search_arxiv":
        try:
            return search_arxiv(
                query=function_call.arguments["query"],
                max_results=function_call.arguments.get("max_results", 5),
            )
        except Exception as e:
            return {"error": f"Failed to search arXiv: {e!s}"}


def ask_gemini(prompt: str, previous_transaction_id: str | None = None):

    # user input to gemini, with previous transaction id if available
    interaction = client.interactions.create(
        input=prompt, previous_interaction_id=previous_transaction_id, **COMMON
    )

    # check if gemini called a function, and handle it if so
    function_call = get_function_call(interaction)
    if function_call is not None:
        result = handle_function_call(function_call)

        interaction = client.interactions.create(
            input=[
                {
                    "type": "function_result",
                    "name": function_call.name,
                    "call_id": function_call.id,
                    "result": [{"type": "text", "text": json.dumps(result)}],
                }
            ],
            previous_interaction_id=interaction.id,
            **COMMON,
        )

    reply = ChatReply.model_validate_json(interaction.output_text)
    reply.transaction_id = interaction.id
    return reply
