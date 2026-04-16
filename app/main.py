from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
from app.agent import process_query
from app.context_manager import ContextManager

app = FastAPI(title="FuelAgent API", description="API for maritime shipping emissions assistant")

context_manager = ContextManager() 

class ChatRequest(BaseModel):
    query: str
    chat_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    sql: Optional[str] = None
    data: Optional[List[dict]] = None
    columns: Optional[List[str]] = None
    error: Optional[str] = None

@app.get("/")
def read_root():
    return {"status": "FuelAgent API is running"}

import json
from fastapi.responses import StreamingResponse

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    def event_generator():
        try:
            for part in process_query(request.query, request.chat_history):
                yield json.dumps(part) + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)
