"""hhParser backend — FastAPI entrypoint."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import CACHE_DIR, CACHE_TTL_HOURS
from app.core import sweep_stale_cache

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)

log = logging.getLogger("hhparser.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    removed = sweep_stale_cache(CACHE_DIR, CACHE_TTL_HOURS)
    log.info("Cache sweep on startup: removed %d stale file(s)", removed)
    yield


app = FastAPI(title="hhParser API", lifespan=lifespan)

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