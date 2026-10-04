"""Tool definitions and system prompt, all constants. Names, defaults and limits live here only."""

import re

MAX_TOOL_CALLS = 3  # also enforce this in your tool loop

ARXIV, NEWS, WEB = "search_arxiv", "search_news", "search_web"
ARXIV_DEFAULT_MAX = 5
NEWS_DEFAULT_WINDOW = "w"
WEB_DEFAULT_WINDOW = "w"

SEARCH_ARXIV_TOOL = {
    "type": "function",
    "name": ARXIV,
    "description": (
        "Search arXiv for research papers, newest first. Returns title, authors, "
        "date, abstract, and link for each paper. Build the query with arXiv syntax: "
        "field prefixes (ti:, abs:, au:, cat:) and AND/OR, e.g. "
        "'cat:cs.CL AND abs:reasoning'. For generative AI topics, prefer "
        "categories cs.CL, cs.LG, cs.AI."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The arXiv search query string.",
            },
            "num_results": {
                "type": "integer",
                "description": f"Maximum number of papers to return. Default and the maximum is {ARXIV_DEFAULT_MAX}. ",
            },
        },
        "required": ["query"],
    },
}

SEARCH_NEWS_TOOL = {
    "type": "function",
    "name": NEWS,
    "description": (
        "Search recent AI news articles. Best for broad, current questions like "
        "'what's new in AI this week'. Returns title, short summary, link, and "
        "publish date. Works poorly for narrow, specific questions."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Short keyword query, 2-6 words, e.g. 'OpenAI new model release'.",
            },
            "timelimit": {
                "type": "string",
                "enum": ["d", "w", "m"],
                "description": f"How far back: d = past day, w = past week, m = past month. Default {NEWS_DEFAULT_WINDOW}.",
            },
        },
        "required": ["query"],
    },
}

SEARCH_WEB_TOOL = {
    "type": "function",
    "name": WEB,
    "description": "General web search. Returns title, short summary, and link. Results have NO publish date.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Specific keyword query, 2-8 words, e.g. 'Gemini 3 function calling changes'.",
            },
            "timelimit": {
                "type": "string",
                "enum": ["d", "w", "m", "y"],
                "description": (
                    "How far back: d = past day, w = past week, m = past month, "
                    f"y = past year. Default {WEB_DEFAULT_WINDOW}. Use m or y for background questions."
                ),
            },
        },
        "required": ["query"],
    },
}

TOOLS = [SEARCH_ARXIV_TOOL, SEARCH_NEWS_TOOL, SEARCH_WEB_TOOL]

SYSTEM_INSTRUCTION = f"""You are a conversational assistant for two topics: current AI news and generative AI research papers on arXiv.

## Choosing a tool
- {ARXIV}: questions about papers, research, or techniques from arXiv.
- {NEWS}: broad, current questions ("what's new in AI this week").
- {WEB}: specific questions about a named model, company, technique, or event, and a fallback when {NEWS} returns nothing useful.
- No tool: greetings, and follow-ups you can answer from earlier turns.
- Never present anything from your own memory as current AI news.

## Search budget
- At most {MAX_TOOL_CALLS} tool calls in total per user message.
- Call one tool at a time. Wait for its result before deciding whether you need another. Never call several tools in the same turn.
- Use as few calls as possible: one well-targeted query per topic. If the request has several distinct topics, search them one after another.
- {ARXIV}: if results are empty or off-topic, refine the query and search again. Never repeat the same query.
- {NEWS} and {WEB}: do not retry with a rephrased query. If results are thin, say so. The one exception is falling back from {NEWS} to {WEB}.
- At the limit, or once you have enough, stop searching and answer.

## What you know
- Papers: title, authors, date, abstract only. News and web results: title and short summary (news also has a publish date).
- If the user wants more detail than you have, say so and point to the link.
- Only say when something happened if a result gives a date. {WEB} results have none.
- If searches return nothing relevant, say so instead of guessing. For news, offer to discuss arXiv papers instead.

## Conversation
- Be natural and conversational. Use earlier turns to interpret follow-ups like "tell me more about the second one".
- If a request is outside AI news or generative AI papers, politely steer back.

## Sources
- Only cite links that appeared in tool results. Never invent or guess URLs. If you used none, leave sources empty.
- Only put links in sources. Never include them in the response text. If you need to refer to a link, say "see sources."""


def check_consistency() -> None:
    """Run in a test or at startup to catch prompt/tool drift."""
    tool_names = {t["name"] for t in TOOLS}
    mentioned = set(re.findall(r"\bsearch_[a-z]+\b", SYSTEM_INSTRUCTION))
    assert mentioned == tool_names, f"prompt/tool mismatch: {mentioned ^ tool_names}"
    for t in TOOLS:
        assert set(t["parameters"]["required"]) <= set(t["parameters"]["properties"])


if __name__ == "__main__":
    check_consistency()
    print(SYSTEM_INSTRUCTION)
