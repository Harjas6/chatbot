# AI News & arXiv Research Chatbot

A full-stack, conversational chatbot built to discuss ongoing AI news and generative AI research papers. It fetches live news using DuckDuckGo and pulls papers from arXiv, giving answers in a fixed three-part format:

1. The response to the user's query.
2. The AI's justification for why the response is appropriate.
3. Direct source links to the news articles or research papers used or found by the model.

**[Skip to How to Run](#how-to-run-the-project)**

## Demo

https://github.com/user-attachments/assets/44531e20-5410-4c11-9f40-7a0bdfe92773

## How It Works & Technical Decisions

### Backend

The backend is built with FastAPI and Google's GenAI SDK. Gemini was chosen because its models offer a free tier. The API receives user messages, applies a system prompt that defines the chatbot's behavior and response requirements passes the request to the chatbot logic, executes any requested tools, and returns a structured response to the frontend.

#### Retrieval-Augmented Generation (RAG)

This chatbot supports Retrieval-Augmented Generation (RAG), allowing users to upload PDF documents and ask questions about their contents. Rather than relying solely on the language model's existing knowledge, the chatbot retrieves relevant passages from uploaded documents and provides them as context when generating responses. It is restricted to PDF only as most research papers tend to be in that format. Uploaded PDFs are saved in backend/data/uploads/, and their embeddings are stored in a local ChromaDB collection.

- **Text Extraction:** Extract text from uploaded PDFs using `pypdf`.
- **Chunking:** Divide the extracted text into 200-token chunks with a 30-token overlap to preserve context across chunk boundaries.
- **Embedding Generation:** Convert each chunk into a numerical vector using the `sentence-transformers/all-MiniLM-L6-v2` embedding model.
- **Vector Storage:** Normalize the embeddings and store them in ChromaDB alongside their corresponding text chunks and source filenames.

When a user submits a question, the original prompt is embedded using the same model and compared against the stored document embeddings. ChromaDB retrieves the closest matching chunks based on vector distance, and a distance threshold filters out results that are not sufficiently relevant. Gemini then generates a response using the original user prompt and any retrieved document passages as context. If no chunks meet the relevance threshold, the chatbot can generate a response without document-derived context.

##### Improvements to RAG

To improve retrieval, I would rewrite or decompose complex user prompts into focused search queries optimized for ChromaDB. This could be achieved using an LLM to identify distinct questions within the user's prompt and generate focused search queries for embedding and retrieval. This would improve retrieval accuracy for prompts involving multiple topics and more lengthy questions. I would also implement more sophisticated document parsing to better handle complex layouts, as well as other file types.

#### Stateless API Design

Since persistent chat history is not needed, multi-turn context is maintained by Gemini servers and referenced using an interaction ID. Each response returns a new ID to the frontend, which sends it back as `previous_interaction_id` on the next request. The backend passes this ID through to Gemini rather than maintaining its own conversation history, so the FastAPI application does not require an in-memory session store or database for conversation state.

#### Structured Output

The chatbot uses a Pydantic model (`ChatReply`) to define the required response structure: `response`, `justification`, and `sources`. This schema is passed to Gemini as the expected structured output format to ensure the backend receives a consistent response structure that the frontend can easily handle.

#### Tool Calling

The chatbot gives Gemini access to three search tools. Based on the user's query, system instructions, and tool descriptions, Gemini determines which tools to call and how to use their results to formulate a response.

- **`search_arxiv`:** Searches for research papers, supporting category filters such as `cat:cs.CL`, `cat:cs.LG`, and `cat:cs.AI`. Results are sorted by submission date, with a maximum of five results.
- **`search_news`:** Searches DuckDuckGo News using configurable time windows (`d`, `w`, and `m`), returning up to five results.
- **`search_web`:** Performs a broader DuckDuckGo search when news results are insufficient or irrelevant, returning up to five results.

DuckDuckGo was chosen over Gemini's native grounding search because it is free to use within this project, whereas combining grounding search with function calling and structured output presented limitations. (Learned that one the hard way.)

**Custom Tool-Calling Loop**

The backend implements tool calling in a custom loop, executing calls sequentially. After each call, the result is returned to Gemini, which can either generate a final response or request another tool call. This allows Gemini to use previously retrieved information to decide whether further searching is necessary, rather than executing every possible search upfront.

To limit API usage and prevent excessive tool execution from increasing latency, each user turn is restricted to three tool calls (`MAX_TOOL_CALLS = 3`). If the limit is reached, `LIMIT_NOTE` instructs Gemini to synthesize a response using the information already retrieved. All tools are then removed from the request, preventing further tool calls during final response generation.

**Future Improvement**

Independent searches, such as an arXiv search and a news search, could be executed in parallel to reduce response time. The implementation would still need to enforce the per-turn tool-call limit.

#### Citation Policy

Prompt instructions require Gemini to place source links in the `sources` field rather than embedding them in the `response` field, and prohibit the model from inventing URLs. Source links are expected to only come from the results returned by the search tools.

This is currently enforced through prompt instructions rather than backend validation. The backend does not independently verify that every URL in `sources` appeared in a tool result. URL validation could be added later by comparing the model's sources against the URLs returned by the tools. No issues ever arose in manual spot checking.

#### Configuration and Testing

Tool definitions, system instructions, and shared configuration are centralized in `chat_config.py`. Shared constants are reused across the tool schemas, prompt, and backend logic to keep limits and defaults consistent. A `check_consistency()` function checks for mismatches between the tools defined for Gemini and those referenced in the system prompt.

The chatbot was tested using `chat_test.py`, which generates a text file containing chatbot responses for manual review. Testing focused on whether responses were semantically correct and whether citations were appropriate and supported by the search results.

### Frontend

The frontend is built with React using TypeScript and Vite. Messages use a discriminated union (`Message = UserMessageData | AIMessageData | ErrorMessageData`) keyed on `role`, allowing user prompts, AI responses, and errors to coexist in a single typed conversation state while preserving their distinct fields. `MessageList` uses the message type to render the appropriate component.

The transaction ID returned by the backend is stored in frontend state and passed back with the next request to maintain multi-turn context. The ID is used internally and is not displayed as part of the conversation.

All styling was prompt-generated with manual tweaks as the goal was just a simple, clear, and scrollable UI that effectively presents the conversation.

## How to Run the Project

### Prerequisites

- **Python 3.10+** (for the FastAPI backend)
- **Node.js v22 LTS** (for the Vite React frontend)
- A **Gemini API Key**
  - You can get one for free from [Google AI Studio](https://aistudio.google.com/apikey) if you do not have one.

You will need two terminal windows open: one for the backend and one for the frontend.

### Environment Setup

You need to set up your environment variables for the backend to communicate with the Gemini API.
In the `backend/` directory, create a `.env` file with the following contents:

```env
GEMINI_API_KEY="your_api_key_here"
MODEL="gemini-3.5-flash-lite"
```

Replace `your_api_key_here` with your actual Gemini API key.

**Note:** This project has only been tested with the **Gemini 3.5 Flash Lite** (`gemini-3.5-flash-lite`) model. Other Gemini 3.x models that support structured output and tool calls may work but are untested. I just like free things.

### 1. Start the Backend (FastAPI)

On first launch, the backend downloads the all-MiniLM-L6-v2 embedding model, so the initial startup takes longer and requires an internet connection.

Open a terminal and run the following commands:

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the Python dependencies
pip install -r requirements.txt

# Launch the FastAPI server
uvicorn main:app --reload
```

_The backend will now be running on `http://127.0.0.1:8000`._

### 2. Start the Frontend (React / Vite)

Open a new terminal window and run:

```bash
# Navigate to the frontend directory
cd frontend

# Install the Node dependencies
npm install

# Launch the Vite development server
npm run dev
```

_The frontend will typically be accessible at `http://localhost:5173` (or `5174`). Click the link in your terminal to open the UI in your browser and start chatting!_
