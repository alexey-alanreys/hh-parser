"""HTTP API.

  POST /api/scan          -> {job_id}
  GET  /api/scan/latest   -> status/progress/result of the most recent job
  GET  /api/scan/{job_id} -> status/progress/result, polled by the client
"""

import asyncio

from fastapi import APIRouter, HTTPException

from app.jobs import Job, job_manager
from app.models import AnalysisResult
from app.schemas import (
    AnalysisResultOut,
    CountItem,
    JobStatusOut,
    ScanCreatedOut,
    ScanRequest,
)

router = APIRouter(prefix="/api")


def _to_result_out(result: AnalysisResult) -> AnalysisResultOut:
    return AnalysisResultOut(
        query=result.query,
        total_vacancies=result.total_vacancies,
        hot_skills=[CountItem(label=s, count=c) for s, c in result.hot_skills],
        hot_keywords=[CountItem(label=w, count=c) for w, c in result.hot_keywords],
    )


def _to_status_out(job: Job) -> JobStatusOut:
    return JobStatusOut(
        job_id=job.id,
        query=job.query,
        status=job.status,
        progress=job.progress,
        result=_to_result_out(job.result) if job.result else None,
        error=job.error,
    )


@router.post("/scan", response_model=ScanCreatedOut)
async def create_scan(request: ScanRequest) -> ScanCreatedOut:
    try:
        request.validate_experience()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    job = job_manager.create(query=request.query)
    asyncio.create_task(job_manager.run(job.id, request))
    return ScanCreatedOut(job_id=job.id)


# Must be registered before /scan/{job_id} — otherwise that dynamic route
# would capture "latest" as a job_id and always 404.
@router.get("/scan/latest", response_model=JobStatusOut)
async def get_latest_scan() -> JobStatusOut:
    job = job_manager.get_latest()
    if job is None:
        raise HTTPException(status_code=404, detail="Ни один скан ещё не запускался")
    return _to_status_out(job)


@router.get("/scan/{job_id}", response_model=JobStatusOut)
async def get_scan(job_id: str) -> JobStatusOut:
    job = job_manager.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job не найден или устарел")
    return _to_status_out(job)