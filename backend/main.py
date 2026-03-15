"""
خادم الوكيل الذكي - FastAPI Server
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from agent import RealAIAgent, LLMClient
import json
from datetime import datetime

app = FastAPI(title="Arabic AI Agent API", version="1.0.0")

# إضافة CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# نماذج البيانات
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Message]] = None

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    iteration_count: int

# إنشاء الوكيل
llm_client = LLMClient()
agent = RealAIAgent(llm_client)

@app.get("/health")
async def health_check():
    """فحص صحة الخادم"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model": agent.llm.model
    }

@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """إرسال رسالة إلى الوكيل"""
    try:
        # تنفيذ الوكيل
        response = agent.think_and_act(request.message)
        
        return ChatResponse(
            response=response,
            timestamp=datetime.now().isoformat(),
            iteration_count=agent.current_iteration
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory")
async def get_memory():
    """الحصول على محتويات الذاكرة"""
    return {
        "short_term": agent.memory.short_term[-10:],  # آخر 10 عناصر
        "long_term": agent.memory.long_term,
        "facts": agent.memory.facts
    }

@app.post("/clear-memory")
async def clear_memory():
    """مسح الذاكرة"""
    agent.memory.short_term = []
    agent.memory.long_term = []
    agent.memory.facts = {}
    return {"status": "Memory cleared"}

@app.get("/tools")
async def get_tools():
    """الحصول على قائمة الأدوات المتاحة"""
    tools = []
    for name, tool in agent.tools.items():
        tools.append({
            "name": name,
            "description": tool.description
        })
    return {"tools": tools}

@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "name": "وكيل الذكاء الاصطناعي العربي المستقل",
        "version": "1.0.0",
        "description": "وكيل ذكاء اصطناعي حقيقي ومستقل تماماً",
        "endpoints": {
            "health": "/health",
            "chat": "/chat (POST)",
            "memory": "/memory (GET)",
            "clear_memory": "/clear-memory (POST)",
            "tools": "/tools (GET)"
        }
    }

if __name__ == "__main__":
    print("🚀 بدء خادم وكيل الذكاء الاصطناعي...")
    print("📍 الخادم يعمل على: http://localhost:8000")
    print("📚 التوثيق: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
