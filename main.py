from fastapi import FastAPI
from scheduler import start_scheduler
from signal_generator import generate_signals

app = FastAPI()

@app.get("/status")
def status():
    return {"message": "TradeSage FX backend is live!"}

@app.get("/signals")
def signals():
    return generate_signals()

# Start 15-min analysis scheduler
start_scheduler()
