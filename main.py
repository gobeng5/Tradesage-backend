from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from scheduler import start_scheduler
from signal_generator import generate_signals
from analyzer import analyze_screenshot

app = FastAPI()

# CORS setup for frontend deployment
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
    contents = await image.read()
    result = analyze_screenshot(contents)
    result["filename"] = image.filename
    return result

# Start recurring 15-minute signal generation
start_scheduler()
