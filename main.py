from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware

from live_signal_generator import generate_live_signals, MANUAL_OVERRIDE_THRESHOLD
from analyzer import analyze_screenshot
from scheduler import start_scheduler
from history import fetch_signal_history
from analytics import get_confidence_trend

import live_signal_generator as signalgen  # for updating threshold

app = FastAPI()

# ✅ CORS setup for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tradesage-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Health check
@app.get("/status")
def status():
    return {"message": "TradeSage FX backend is live and streaming market intelligence!"}

# ✅ Live signal engine
@app.get("/signals")
def signals():
    return generate_live_signals()

# ✅ Screenshot-based analysis
@app.post("/analyze")
async def analyze_image(image: UploadFile = File(...)):
    contents = await image.read()
    result = analyze_screenshot(contents)
    result["filename"] = image.filename
    return result

# ✅ Logged signal history
@app.get("/history")
def history():
    return {"history": fetch_signal_history()}

# ✅ Confidence trend insights
@app.get("/analytics/confidence")
def confidence(pair: str = None, limit: int = 100):
    return {"trend": get_confidence_trend(pair, limit)}

# ✅ Manual override threshold via frontend toggle
@app.post("/config/threshold")
async def update_threshold(request: Request):
    payload = await request.json()
    value = payload.get("override_threshold")
    if isinstance(value, (float, int)):
        signalgen.MANUAL_OVERRIDE_THRESHOLD = float(value)
        return {
            "status": "success",
            "threshold": signalgen.MANUAL_OVERRIDE_THRESHOLD
        }
    return {"status": "error", "message": "Invalid override value"}

# ✅ Scheduler: Cron jobs or heartbeat loops
start_scheduler()
