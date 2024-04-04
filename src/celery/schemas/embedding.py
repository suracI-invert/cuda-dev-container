from pydantic import BaseModel

class EmbeddingRequest(BaseModel):
    text: str

class EmbeddingResponse(BaseModel):
    task_id: str
    text: str