"""hhParser backend — FastAPI entrypoint."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)

app = FastAPI(title="hhParser API")

# CORS is only needed for `vite dev` on :5173; nginx handles same-origin in prod.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
