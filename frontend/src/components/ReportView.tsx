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
          <h1>Результаты: {result.query}</h1>
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
    </div>
  );
}
