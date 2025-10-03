from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd, numpy as np
from pathlib import Path

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset
DATA_FILE = Path(__file__).parent / "q-vercel-latency.json"
df = pd.read_json(DATA_FILE)

@app.get("/")
async def root():
    return {"message": "Vercel Latency Analytics API is running."}

@app.post("/api/")
async def get_latency_stats(request: Request):
    payload = await request.json()
    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 200)
    results = []

    for region in regions:
        r = df[df["region"] == region]
        if not r.empty:
            results.append({
                "region": region,
                "avg_latency": round(r["latency_ms"].mean(), 2),
                "p95_latency": round(np.percentile(r["latency_ms"], 95), 2),
                "avg_uptime": round(r["uptime_pct"].mean(), 3),
                "breaches": int((r["latency_ms"] > threshold).sum())
            })
    return {"regions": results}
