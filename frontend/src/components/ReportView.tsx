import { exportCsv, exportJson } from '../api/export';
import type { AnalysisResult } from '../types';

import RankedList from './RankedList';

interface Props {
  result: AnalysisResult;
}

export default function ReportView({ result }: Props): React.JSX.Element {
  return (
    <div className='report'>
      <div className='report-header'>
        <div>
          <h1>«{result.query}»</h1>
          <p className='report-meta'>
            Проанализировано вакансий: {result.total_vacancies}
          </p>
        </div>
        <div className='export-actions'>
          <button
            className='btn-secondary'
            onClick={() => exportJson(result)}
          >
            Экспорт JSON
          </button>
          <button
            className='btn-secondary'
            onClick={() => exportCsv(result)}
          >
            Экспорт CSV
          </button>
        </div>
      </div>

      <div className='report-grid'>
        <RankedList
          items={result.hot_skills}
          title='🔥 Горячие навыки'
        />
        <RankedList
          items={result.hot_keywords}
          title='🔑 Горячие ключевые слова'
        />
      </div>

      <details className='full-lists'>
        <summary>
          Полные списки (всего навыков: {result.all_skills.length}, слов:{' '}
          {result.all_keywords.length})
        </summary>
        <div className='full-lists-grid'>
          <ul className='compact-list'>
            {result.all_skills.map((s) => (
              <li key={s.label}>
                <span>{s.label}</span>
                <span className='compact-count'>{s.count}</span>
              </li>
            ))}
          </ul>
          <ul className='compact-list'>
            {result.all_keywords.map((k) => (
              <li key={k.label}>
                <span>{k.label}</span>
                <span className='compact-count'>{k.count}</span>
              </li>
            ))}
          </ul>
        </div>
      </details>
    </div>
  );
}
