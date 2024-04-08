from pydantic import BaseModel

class QueryRequest(BaseModel):
    text: str

class QueryResponse(BaseModel):
    task_id: str
    text: str