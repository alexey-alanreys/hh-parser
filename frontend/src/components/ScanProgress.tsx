import type { JobProgress, JobStage } from '../types';

const STAGE_LABELS: Record<JobStage, string> = {
  collecting: 'Сбор списка вакансий',
  enriching: 'Загрузка описаний и навыков',
  analyzing: 'Частотный анализ',
};

interface Props {
  query: string;
  progress: JobProgress | null;
}

export default function ScanProgress({
  query,
  progress,
}: Props): React.JSX.Element {
  const stage = progress?.stage ?? 'collecting';
  const current = progress?.current ?? 0;
  const total = progress?.total ?? 0;
  const pct =
    total > 0 ? Math.min(100, Math.round((current / total) * 100)) : 0;

  return (
    <div
      aria-live='polite'
      className='progress-panel'
      role='status'
    >
      <div className='progress-query'>Обрабатывается: «{query}»</div>
      <div className='progress-label'>
        <span>{STAGE_LABELS[stage]}</span>
        {total > 0 && (
          <span className='progress-count'>
            {current}/{total}
          </span>
        )}
      </div>
      <div className='progress-track'>
        <div
          className='progress-fill'
          style={{ width: `${total > 0 ? pct : 6}%` }}
        />
      </div>
    </div>
  );
}
