from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from scheduler import start_scheduler
from signal_generator import generate_signals
import random

app = FastAPI()

# Allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tradesage-frontend.onrender.com"],
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

@app.post("/analyze")
async def analyze_image(image: UploadFile = File(...)):
    # For now, mock analysis results
    mock_strategy = random.choice(["Breakout", "Pullback", "Reversal", "Momentum"])
    confidence = round(random.uniform(0.65, 0.95), 2)

    return {
        "filename": image.filename,
        "strategy_detected": mock_strategy,
        "confidence_score": confidence,
        "comment": f"Screenshot appears to reflect a {mock_strategy} setup with {int(confidence * 100)}% confidence."
    }

# Start 15-min analysis scheduler
start_scheduler()
