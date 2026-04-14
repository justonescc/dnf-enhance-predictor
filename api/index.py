from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"service": "DNF Enhancement Predictor API", "version": "test"}

@app.get("/api/probabilities")
def probabilities():
    return {"status": "ok", "enhance": {"+10": 0.4}, "badge": {"7": 0.5}}

@app.post("/api/predict")
def predict():
    return {"status": "ok", "predicted_rate": 0.5}
