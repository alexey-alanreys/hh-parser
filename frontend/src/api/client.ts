import type { JobStatusOut, ScanRequest } from '../types';

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!resp.ok) {
    const body: unknown = await resp.json().catch(() => null);
    const detail =
      body !== null && typeof body === 'object' && 'detail' in body
        ? body.detail
        : undefined;
    throw new ApiError(
      resp.status,
      typeof detail === 'string' ? detail : resp.statusText,
    );
  }
  return resp.json() as Promise<T>;
}

export function createScan(payload: ScanRequest): Promise<{ job_id: string }> {
  return request('/api/scan', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getScanStatus(jobId: string): Promise<JobStatusOut> {
  return request(`/api/scan/${jobId}`);
}

export function getLatestScan(): Promise<JobStatusOut> {
  return request('/api/scan/latest');
}

const POLL_INTERVAL_MS = 1200;

/**
 * Polls job status until it reaches done/error.
 * onUpdate fires on every tick, including intermediate running states.
 */
export async function pollScan(
  jobId: string,
  onUpdate: (status: JobStatusOut) => void,
  signal?: AbortSignal,
): Promise<JobStatusOut> {
  while (true) {
    if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
    const status = await getScanStatus(jobId);
    onUpdate(status);
    if (status.status === 'done' || status.status === 'error') {
      return status;
    }
    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
  }
}
