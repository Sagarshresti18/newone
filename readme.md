# How to Run My Rasa Chatbot Project

## Quick Start (Windows)
1. Open Command Prompt/PowerShell
2. Navigate to project: `cd "C:\Users\sagar shresti\Desktop\CHATBOTPRO"`
3. Activate virtual environment: `venv\Scripts\activate`
4. Run startup script: `run_chatbot.bat`
5. Wait for all servers to start
6. Open browser: http://localhost:8000

## Manual Start (3 terminals needed)

### Terminal 1 - Rasa Server
```bash
cd "C:\Users\sagar shresti\Desktop\CHATBOTPRO"
venv\Scripts\activate
rasa run --enable-api --cors "*" --port 5005
```

### Terminal 2 - Actions Server  
```bash
cd "C:\Users\sagar shresti\Desktop\CHATBOTPRO"
venv\Scripts\activate  
rasa run actions
```

### Terminal 3 - Web Server
```bash
cd "C:\Users\sagar shresti\Desktop\CHATBOTPRO"
venv\Scripts\activate
python main.py
```

### Then visit: http://localhost:8000

## Troubleshooting

### If servers don't start:
- Make sure you're in the right directory
- Check if virtual environment exists: `ls venv/` or `dir venv`
- Retrain model if needed: `rasa train`

### If ports are busy:
- Check running processes: `netstat -ano | findstr :5005`
- Kill processes or restart computer

### If dependencies are missing:
```bash
pip install fastapi uvicorn websockets httpx rasa rasa-sdk
```

## File Structure
```
CHATBOTPRO/
├── venv/                 # Virtual environment
├── models/              # Trained Rasa models
├── data/                # Training data
├── actions/             # Custom actions
├── main.py              # FastAPI server
├── index.html           # Chat interface
├── run_chatbot.bat      # Startup script
└── config.yml           # Rasa configuration
```

## Important Notes
- Always activate virtual environment first
- Start servers in order: Rasa → Actions → FastAPI
- Wait between starting servers
- Access via localhost:8000 (not 0.0.0.0:8000)
