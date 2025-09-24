# How to Run My Rasa Chatbot Project

## Quick Start (Windows)
1. Open Command Prompt/PowerShell
2. Navigate to project: `cd "newone"`
3. Activate virtual environment: `venv\Scripts\activate`
4. Run startup script: `run_chatbot.bat`
5. Wait for all servers to start
6. Open browser: http://localhost:8000


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

