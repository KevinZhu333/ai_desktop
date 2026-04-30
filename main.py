import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.chat.chat import Chat

if __name__ == "__main__":
    app = FastAPI(title="AI AGENT API")
    chat = Chat()

    class InstructionRequest(BaseModel):
        user_id: str
        query: str
        history: list

    @app.post("/ai_agent")
    async def detect_intent_api(req: InstructionRequest):
        try:
            return chat.chat(req.user_id, req.query, req.history)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    uvicorn.run(app, host="0.0.0.0", port=8000)