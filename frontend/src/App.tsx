import { useEffect, useRef, useState } from 'react';

import { ApiError, createScan, getLatestScan, pollScan } from './api/client';
import ReportView from './components/ReportView';
import ScanProgress from './components/ScanProgress';
import SearchForm from './components/SearchForm';
import type { AnalysisResult, JobProgress, ScanRequest } from './types';

import './App.css';

type ViewState =
  | { kind: 'idle' }
  | { kind: 'running'; query: string; progress: JobProgress | null }
  | { kind: 'done'; result: AnalysisResult }
  | { kind: 'error'; message: string };

export default function App(): React.JSX.Element {
  const [state, setState] = useState<ViewState>({ kind: 'idle' });
  const abortRef = useRef<AbortController | null>(null);

  async function trackJob(
    jobId: string,
    query: string,
    signal: AbortSignal,
  ): Promise<void> {
    setState({ kind: 'running', query, progress: null });

    try {
      const final = await pollScan(
        jobId,
        (status) => {
          if (status.status === 'running' || status.status === 'pending') {
            setState({
              kind: 'running',
              query: status.query,
              progress: status.progress,
            });
          }
        },
        signal,
      );

      if (final.status === 'done' && final.result) {
        setState({ kind: 'done', result: final.result });
      } else {
        setState({
          kind: 'error',
          message: final.error ?? 'Скан завершился с ошибкой',
        });
      }
    } catch (e) {
      if ((e as DOMException).name === 'AbortError') return;

      if (e instanceof ApiError && e.status === 404) {
        // Job evicted (TTL, see backend/app/jobs.py) or server restarted —
        // benign from the user's point of view, not an error to alarm them with.
        setState({ kind: 'idle' });
        return;
      }

      setState({
        kind: 'error',
        message: e instanceof Error ? e.message : 'Неизвестная ошибка',
      });
    }
  }

  useEffect(() => {
    return () => abortRef.current?.abort();
  }, []);

  // No client-side storage: the server always knows its most recent job
  // (see JobManager.get_latest in backend/app/jobs.py), so a fresh page
  // load — reload, closed-and-reopened tab, new tab — recovers it by just
  // asking. A 404 here means no scan has ever run on this server instance,
  // which is the normal cold-start case, not an error.
  useEffect(() => {
    const controller = new AbortController();
    abortRef.current = controller;

    getLatestScan()
      .then((status) => {
        if (status.status === 'done' && status.result) {
          setState({ kind: 'done', result: status.result });
        } else if (status.status === 'error') {
          setState({
            kind: 'error',
            message: status.error ?? 'Скан завершился с ошибкой',
          });
        } else {
          void trackJob(status.job_id, status.query, controller.signal);
        }
      })
      .catch((e: unknown) => {
        if (!(e instanceof ApiError && e.status === 404)) {
          setState({
            kind: 'error',
            message: e instanceof Error ? e.message : 'Неизвестная ошибка',
          });
        }
      });
  }, []);

  async function handleSubmit(payload: ScanRequest): Promise<void> {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const { job_id } = await createScan(payload);
      await trackJob(job_id, payload.query, controller.signal);
    } catch (e) {
      if ((e as DOMException).name === 'AbortError') return;
      setState({
        kind: 'error',
        message: e instanceof Error ? e.message : 'Неизвестная ошибка',
      });
    }
  }

  return (
    <div className='app-shell'>
      <header className='app-header'>
        <span className='eyebrow'>hh.ru · сканер вакансий</span>
        <h1 className='brand'>hhParser</h1>
        <p className='tagline'>
          Что чаще всего просят в вакансиях hh.ru — без ручного чтения сотни
          страниц.
        </p>
      </header>

      <SearchForm
        disabled={state.kind === 'running'}
        onSubmit={(payload) => {
          void handleSubmit(payload);
        }}
      />

      {state.kind === 'running' && (
        <ScanProgress
          progress={state.progress}
          query={state.query}
        />
      )}

      {state.kind === 'error' && (
        <div
          className='error-panel'
          role='alert'
        >
          {state.message}
        </div>
      )}

      {state.kind === 'done' && <ReportView result={state.result} />}
    </div>
  );
}
