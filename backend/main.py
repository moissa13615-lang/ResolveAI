
from fastapi import FastAPI

app = FastAPI(
    title="ResolveAI API",
    description="AI-Powered IT Help Desk and Automation Platform",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to ResolveAI!",
        "status": "running",
        "project": "AI-Powered IT Help Desk"
    }
