import { useEffect, useRef, useState } from 'react';

import { createScan, pollScan } from './api/client';
import ReportView from './components/ReportView';
import ScanProgress from './components/ScanProgress';
import SearchForm from './components/SearchForm';
import type { AnalysisResult, JobProgress, ScanRequest } from './types';

import './App.css';

type ViewState =
  | { kind: 'idle' }
  | { kind: 'running'; progress: JobProgress | null }
  | { kind: 'done'; result: AnalysisResult }
  | { kind: 'error'; message: string };

export default function App(): React.JSX.Element {
  const [state, setState] = useState<ViewState>({ kind: 'idle' });
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    return () => abortRef.current?.abort();
  }, []);

  async function handleSubmit(payload: ScanRequest): Promise<void> {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setState({ kind: 'running', progress: null });

    try {
      const { job_id } = await createScan(payload);
      const final = await pollScan(
        job_id,
        (status) => {
          if (status.status === 'running' || status.status === 'pending') {
            setState({ kind: 'running', progress: status.progress });
          }
        },
        controller.signal,
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
      setState({
        kind: 'error',
        message: e instanceof Error ? e.message : 'Неизвестная ошибка',
      });
    }
  }

  return (
    <div className='app-shell'>
      <header className='app-header'>
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

      {state.kind === 'running' && <ScanProgress progress={state.progress} />}

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
