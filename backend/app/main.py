"""FastAPI 应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.predict import router

app = FastAPI(
    title="DNF增幅概率预测器 API",
    description="基于马尔可夫链、HMM、贝叶斯更新的增幅概率预测服务",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"service": "DNF Enhancement Predictor API", "version": "1.0.0"}