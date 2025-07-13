from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from live_signal_generator import generate_live_signals
from analyzer import analyze_screenshot
from scheduler import start_scheduler
from history import fetch_signal_history

app = FastAPI()

# ✅ CORS setup for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tradesage-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Health check endpoint
@app.get("/status")
def status():
    return {"message": "TradeSage FX backend is live and streaming market intelligence!"}

# ✅ Live signal endpoint from Alpha Vantage
@app.get("/signals")
def signals():
    return generate_live_signals()

# ✅ Screenshot analysis endpoint
@app.post("/analyze")
async def analyze_image(image: UploadFile = File(...)):
    contents = await image.read()
    result = analyze_screenshot(contents)
    result["filename"] = image.filename
    return result

# ✅ Signal history endpoint from SQLite
@app.get("/history")
def history():
    return {"history": fetch_signal_history()}

# ✅ Internal scheduler (e.g., background tasks or refresh hooks)
start_scheduler()
