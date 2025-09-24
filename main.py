from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import asyncio
import logging
from typing import Dict, List
import uuid
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Rasa Chatbot API", description="FastAPI server for Rasa chatbot with web interface")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
RASA_SERVER_URL = "http://localhost:5005"
RASA_WEBHOOK_URL = f"{RASA_SERVER_URL}/webhooks/rest/webhook"

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connection established for session: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket connection closed for session: {session_id}")

    async def send_personal_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the main HTML page"""
    try:
        with open("index.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        
        # Replace the Rasa WebChat configuration to use our WebSocket endpoint
        modified_html = html_content.replace(
            "socketUrl: 'http://localhost:5005',",
            f"socketUrl: 'ws://localhost:8000/ws',"
        ).replace(
            "socketPath: '/socket.io/',",
            "socketPath: '/',"
        )
        
        return HTMLResponse(content=modified_html)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="index.html file not found")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Rasa Chatbot API"}

@app.get("/rasa/status")
async def check_rasa_status():
    """Check if Rasa server is running"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{RASA_SERVER_URL}/api/version")
            if response.status_code == 200:
                return {"status": "connected", "rasa_version": response.json()}
            else:
                return {"status": "error", "message": f"Rasa server returned status {response.status_code}"}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}

@app.post("/chat")
async def chat_with_rasa(message: dict):
    """Direct REST API endpoint for chatting with Rasa"""
    try:
        user_message = message.get("message", "")
        sender_id = message.get("sender", str(uuid.uuid4()))
        
        payload = {
            "sender": sender_id,
            "message": user_message
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(RASA_WEBHOOK_URL, json=payload)
            
            if response.status_code == 200:
                bot_responses = response.json()
                return {
                    "status": "success",
                    "responses": bot_responses,
                    "sender": sender_id
                }
            else:
                return {
                    "status": "error",
                    "message": f"Rasa server error: {response.status_code}",
                    "detail": response.text
                }
                
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, session_id)
    
    try:
        # Send welcome message
        welcome_payload = {
            "sender": "bot",
            "message": "Hello! I'm your AI assistant. How can I help you today?",
            "type": "text"
        }
        await websocket.send_text(json.dumps(welcome_payload))
        
        while True:
            # Receive message from WebSocket
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            logger.info(f"Received message from {session_id}: {user_message}")
            
            if user_message:
                # Send message to Rasa
                try:
                    payload = {
                        "sender": session_id,
                        "message": user_message
                    }
                    
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        response = await client.post(RASA_WEBHOOK_URL, json=payload)
                        
                        if response.status_code == 200:
                            bot_responses = response.json()
                            
                            # Send each bot response back through WebSocket
                            for bot_response in bot_responses:
                                response_payload = {
                                    "sender": "bot",
                                    "message": bot_response.get("text", ""),
                                    "type": "text"
                                }
                                
                                # Handle buttons, images, etc. if present
                                if "buttons" in bot_response:
                                    response_payload["buttons"] = bot_response["buttons"]
                                if "image" in bot_response:
                                    response_payload["image"] = bot_response["image"]
                                    response_payload["type"] = "image"
                                
                                await websocket.send_text(json.dumps(response_payload))
                        else:
                            # Send error message
                            error_payload = {
                                "sender": "bot",
                                "message": "Sorry, I'm having trouble connecting to the server. Please try again.",
                                "type": "error"
                            }
                            await websocket.send_text(json.dumps(error_payload))
                            
                except httpx.RequestError as e:
                    logger.error(f"Request error: {str(e)}")
                    error_payload = {
                        "sender": "bot",
                        "message": "Sorry, I'm currently unavailable. Please ensure the Rasa server is running.",
                        "type": "error"
                    }
                    await websocket.send_text(json.dumps(error_payload))
                    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {str(e)}")
        manager.disconnect(session_id)

@app.websocket("/ws")
async def websocket_endpoint_no_session(websocket: WebSocket):
    """WebSocket endpoint without session ID (generates one automatically)"""
    session_id = str(uuid.uuid4())
    await websocket_endpoint(websocket, session_id)

# Serve static files (if you have CSS, JS, images, etc.)
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Check Rasa server connection on startup"""
    logger.info("Starting FastAPI server...")
    
    # Check if Rasa server is accessible
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{RASA_SERVER_URL}/api/version")
            if response.status_code == 200:
                logger.info("✅ Rasa server is accessible")
            else:
                logger.warning("⚠️ Rasa server returned non-200 status")
    except Exception as e:
        logger.warning(f"⚠️ Could not connect to Rasa server: {str(e)}")
        logger.info("Make sure to start Rasa server with: rasa run --enable-api --cors '*'")

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting FastAPI server...")
    print("📋 Make sure you have:")
    print("   1. Trained your Rasa model: rasa train")
    print("   2. Started Rasa server: rasa run --enable-api --cors '*'")
    print("   3. Started action server: rasa run actions (if you have custom actions)")
    print("\n🌐 Your chatbot will be available at: http://localhost:8000")
    print("🔧 API docs available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )