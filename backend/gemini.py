import json
import os

from dotenv import load_dotenv
from google import genai
from models import ChatReply
from my_arxiv import search_arxiv

load_dotenv()
MAX_TOOL_CALLS = 3

LIMIT_NOTE = """Tool limit reached. Do not call any more tools. Using only the results
    you already have, write your final reply in the required format. If the
    results were empty or irrelevant, say so instead of guessing. 
    Tell the user this is why you could not get all the info they needed"""

SYSTEM_INSTRUCTION = f"""You are a conversational assistant that discusses two topics: ongoing AI news and generative AI research papers on arXiv.

Tools:
- Use Google Search for current AI news and recent developments. Aim to use the LEAST amount of searches possible.
- Use the search_arxiv tool for papers, research, or techniques from arXiv.
- Use as few searches as possible. Aim to cover the whole request with one well-targeted query per tool. If you genuinely need several separate searches, make them together in the same turn rather than one after another.
- Only search again if the previous result was empty or clearly irrelevant, and refine the query each time rather than repeating it.
- You may call search_arxiv at most {MAX_TOOL_CALLS} times in total while answering a single user message. Once you have enough, or reach that limit, stop calling tools and write your final reply using what you have. If the searches returned nothing relevant, say so in the response instead of guessing.
- Never answer questions about current news from memory as if the information were current. If web search returns nothing usable, say so.

Scope:
- Answer any question about AI news, not just generative AI.
- For papers, focus on generative AI. If the user asks about a paper outside generative AI, you may answer briefly, but mention that your focus is generative AI research.
- If a request is unrelated to AI, do not use any tools. Politely explain what you cover, suggest a relevant topic (for example, recent AI news or a generative AI paper), and still return all three parts, with sources left empty.

Conversation:
- Be conversational and natural. Use the earlier turns of the conversation to interpret follow-up questions (for example "tell me more about the second one").
- For arXiv papers, you only have each paper's title, authors, date, and abstract. When discussing a paper, base your answers on those. If the user asks for details the abstract doesn't cover, say you only have the abstract and point them to the paper's link.
- For news, mention publication dates where available, since news is time-sensitive.

Every reply must have three parts:
1. response: the answer to the user's message, taking previous turns into account.
2. justification: a short explanation of why this response is appropriate, including whether you used a search, which one, and why.
3. sources: a list of links you actually used.

Rules for sources:
- Only include links that appeared in arXiv results or web search results. Never invent or guess URLs.
- If you did not use any sources (for example a greeting, an off-topic redirect, or a follow-up answered from earlier context), return an empty list.
- If a search returns nothing relevant, say so in the response instead of guessing. Do not add sources in that case."""

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
tools = [search_arxiv_tool, {"type": "google_search"}]


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
    if function_call.name == "search_arxiv":
        try:
            return search_arxiv(
                query=function_call.arguments["query"],
                max_results=function_call.arguments.get("max_results", 5),
            )
        except Exception as e:
            return {"error": f"Failed to search arXiv: {e!s}"}


def collect_grounded_sources(interaction, sources):
    # pulled from the gemini docs page
    for step in interaction.steps:
        if step.type == "model_output":
            for block in step.content:
                if block.type == "text" and block.annotations:
                    for annotation in block.annotations:
                        if annotation.type == "url_citation":
                            sources[annotation.url] = annotation.title


def send_function_result(interaction, function_call, limit_reached, result):
    return client.interactions.create(
        input=[
            {
                "type": "function_result",
                "name": function_call.name,
                "call_id": function_call.id,
                "result": [{"type": "text", "text": json.dumps(result)}],
            }
        ],
        previous_interaction_id=interaction.id,
        **(COMMON_NO_TOOLS if limit_reached else COMMON),
    )


def ask_gemini(prompt: str, previous_transaction_id: str | None = None):
    grounded_sources: dict[str, str] = {}
    # user input to gemini, with previous transaction id if available
    interaction = client.interactions.create(
        input=prompt, previous_interaction_id=previous_transaction_id, **COMMON
    )
    collect_grounded_sources(interaction, grounded_sources)
    # check if gemini called a function, and handle it if so
    rounds = 0
    while (function_call := get_function_call(interaction)) is not None:
        rounds += 1
        result = handle_function_call(function_call)

        limit_reached = rounds >= MAX_TOOL_CALLS
        if limit_reached:
            result = {"result": result, "note": LIMIT_NOTE}

        interaction = send_function_result(
            interaction, function_call, limit_reached, result
        )
        collect_grounded_sources(interaction, grounded_sources)
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
    for url in grounded_sources:
        if url not in reply.sources:
            reply.sources.append(url)
    reply.transaction_id = interaction.id
    return reply
