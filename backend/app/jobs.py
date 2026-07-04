"""In-memory job store and background runner for the scraping pipeline.

Job state lives in the process, so uvicorn must run with --workers 1
(see docker/supervisord.conf) — otherwise jobs created on one worker are
invisible to the others. State is also lost on container restart, which
is acceptable for a single-user, self-hosted tool.

The pipeline itself is blocking (requests, BeautifulSoup), so it runs in
a separate thread via asyncio.to_thread to avoid blocking the event loop.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field

from app.models import AnalysisResult
from app.pipeline import NoVacanciesFoundError, run_pipeline
from app.schemas import JobProgress, JobStage, JobStatus, ScanRequest

log = logging.getLogger("hhparser.jobs")

JOB_TTL_SECONDS = 3600  # jobs older than this are evicted on the next create()


@dataclass
class Job:
    id: str
    status: JobStatus = JobStatus.PENDING
    progress: JobProgress | None = None
    result: AnalysisResult | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}

    def _evict_stale(self) -> None:
        cutoff = time.time() - JOB_TTL_SECONDS
        stale = [jid for jid, j in self._jobs.items() if j.created_at < cutoff]
        for jid in stale:
            del self._jobs[jid]

    def create(self) -> Job:
        self._evict_stale()
        job = Job(id=str(uuid.uuid4()))
        self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    async def run(self, job_id: str, request: ScanRequest) -> None:
        import asyncio

        job = self._jobs[job_id]
        job.status = JobStatus.RUNNING

        def on_progress(stage: JobStage, current: int, total: int) -> None:
            job.progress = JobProgress(stage=stage, current=current, total=total)

        try:
            result = await asyncio.to_thread(run_pipeline, request, on_progress)
            job.result = result
            job.status = JobStatus.DONE
        except NoVacanciesFoundError as e:
            job.status = JobStatus.ERROR
            job.error = str(e)
        except Exception as e:  # noqa: BLE001 — worker boundary, must not crash the process
            log.exception("Job %s failed", job_id)
            job.status = JobStatus.ERROR
            job.error = f"Внутренняя ошибка: {e}"


job_manager = JobManager()
