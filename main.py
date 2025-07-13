from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scheduler import start_scheduler
from signal_generator import generate_signals

app = FastAPI()

# CORS setup to allow frontend access from Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tradesage-frontend.onrender.com"],  # your deployed frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/status")
def status():
    return {"message": "TradeSage FX backend is live!"}

@app.get("/signals")
def signals():
    return generate_signals()

# Start 15-min analysis scheduler
start_scheduler()
