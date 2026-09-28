from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    previous_transaction_id: str | None = None


class ChatReply(BaseModel):
    response: str = Field(
        description="The conversational reply to the user's message, taking prior turns in the conversation into account."
    )
    justification: str = Field(
        description="A brief explanation of why this response is an appropriate answer to the user's query."
    )
    sources: list[str] = Field(
        description="URLs of the sources (AI news articles or arXiv papers) used to inform the response."
    )
    transaction_id: str
