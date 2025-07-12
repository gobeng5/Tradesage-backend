from fastapi import FastAPI

app = FastAPI()

@app.get("/status")
def status():
    return {"message": "TradeSage FX backend is live!"}
