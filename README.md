# AI News & arXiv Research Chatbot

A full-stack conversational chatbot for discussing current AI news and generative AI research papers. It pulls live news from DuckDuckGo and papers from arXiv, and can answer questions about PDFs you upload (RAG). Every answer has three parts:

1. **Response** to the user's query
2. **Justification** for why the response is appropriate
3. **Sources**: links to the news articles or papers used

**Stack:** FastAPI · Google GenAI SDK (Gemini) · ChromaDB · sentence-transformers · React + TypeScript + Vite

**[Skip to How to Run](#how-to-run-the-project)**

## Demo

https://github.com/user-attachments/assets/44531e20-5410-4c11-9f40-7a0bdfe92773

## How It Works

### RAG (PDF Uploads)

Users can upload PDFs and ask questions about them. Only PDFs are supported, as most research papers are in that format. Files are saved in `backend/uploads/`, and embeddings go in a local ChromaDB collection.

**Indexing:**

1. Extract text with `pypdf`
2. Split into 200-token chunks with 30-token overlap, using the embedding model's own tokenizer so no chunk exceeds its input limit
3. Embed each chunk with `sentence-transformers/all-MiniLM-L6-v2` and normalize
4. Store in ChromaDB with the chunk text and source filename

**Retrieval:** the user's prompt is embedded with the same model, and ChromaDB returns the closest chunks. A distance threshold (currently 1.0, about cosine similarity 0.5 for normalized vectors) drops chunks that aren't relevant. The remaining chunks are wrapped in tagged blocks appended to the user's message. If none pass, Gemini answers without document context.

**Prompt safety:** the system prompt tells Gemini to treat excerpts as data, never as instructions, as a defense against prompt injection from uploaded files. Gemini can answer from the excerpts alone or combine them with live search.

**Limitations**

- **Query rewriting:** the prompt is embedded as-is, so long or multi-topic questions retrieve poorly. An LLM could split them into focused queries.
- **Retrieval on every message:** chunks are fetched before Gemini decides whether the question relates to a document.
- **History growth:** excerpts are added to the user message, so they likely accumulate in the history Gemini stores over a long chat.
- **Document parsing:** `pypdf` struggles with two-column layouts, equations and headers or footers, and does no OCR for scanned PDFs. Better parsing would give cleaner chunks.
- **File types:** PDF only. Word, text and markdown could be added.

### Backend

FastAPI receives each message, applies the system prompt, runs any tools Gemini requests, and returns a structured reply. Gemini was chosen for its free tier.

- **Structured output:** a Pydantic model (`ChatReply`) defines `response`, `justification` and `sources`, and is passed to Gemini as the output schema so the frontend always gets a consistent shape.
- **Stateless API:** multi-turn context lives on Gemini's servers. Each reply returns an interaction ID, which the frontend sends back as `previous_interaction_id`. The backend keeps no session store or database for conversations.
- **Configuration:** tool definitions, the system prompt and shared constants live in `chat_config.py`. A `check_consistency()` function catches mismatches between the tools defined for Gemini and those named in the prompt.

### Tool Calling

Gemini chooses from three tools based on the query, system prompt and tool descriptions:

- **`search_arxiv`:** papers, with category filters (e.g. `cat:cs.LG`), sorted by submission date, up to 5 results
- **`search_news`:** DuckDuckGo News with time windows (`d`, `w`, `m`), up to 5 results
- **`search_web`:** broader DuckDuckGo search when news is thin or irrelevant, up to 5 results

DuckDuckGo is used instead of Gemini's native grounding search because it is free, whereas combining grounding with function calling and structured output was not (learned that the hard way).

**Custom tool loop:** calls run sequentially, and each result goes back to Gemini, which either answers or requests another call. This lets it decide from what it already has instead of searching everything upfront. Each turn is capped at `MAX_TOOL_CALLS = 3` to avoid hitting API rate limits and to keep latency down. At the cap, `LIMIT_NOTE` tells Gemini to answer from what it has, and all tools are removed from the request.

### Citations

The prompt requires links to go in `sources` (never in the response text) and forbids inventing URLs. This is enforced by prompt only; the backend does not check that each URL appeared in a tool result. No problems appeared in manual spot checks.

Uploaded documents have no public URL, so they are never put in `sources`. Gemini names the file in the response text instead.

### Frontend

React with TypeScript and Vite. A discriminated union keyed on `role` lets user messages, AI replies and status messages share one typed conversation state, and `MessageList` renders the right component for each. The interaction ID is kept in state and sent with each request. Styling was prompt-generated with manual tweaks; the goal was a simple, clear, scrollable UI.

### Testing

`chat_test.py` runs a set of prompts and writes the chatbot's responses to a text file for manual review, checking that answers are correct and citations are supported by the search results.

## Other Future Work

- **URL validation:** check that every URL in `sources` appeared in a tool result.
- **Parallel tool calls:** run independent searches (e.g. arXiv and news) at once while still enforcing the per-turn cap.

## How to Run the Project

**Prerequisites:** Python 3.10+, Node.js v22 LTS, and a [Gemini API key](https://aistudio.google.com/apikey) (free).

**1. Configure the backend.** Create `backend/.env`:

```env
GEMINI_API_KEY="your_api_key_here"
MODEL="gemini-3.5-flash-lite"
```

Only tested with `gemini-3.5-flash-lite`. Other Gemini 3.x models that support structured output and tool calls may work.

**2. Start the backend** (terminal 1):

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Runs on `http://127.0.0.1:8000`. On first launch it downloads the `all-MiniLM-L6-v2` embedding model, so startup is slower and needs an internet connection.

**3. Start the frontend** (terminal 2):

```bash
cd frontend
npm install
npm run dev
```

Usually at `http://localhost:5173`. If Vite picks 5174 instead, update the allowed origin (CORS) in `backend/main.py`.
