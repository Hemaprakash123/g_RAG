from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    doc_id: str

class QueryResponse(BaseModel):
    answer: str