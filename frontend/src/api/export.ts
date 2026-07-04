import type { AnalysisResult, CountItem } from '../types';

function downloadBlob(content: string, filename: string, mime: string): void {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function slug(query: string): string {
  return query
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '_')
    .replace(/[^\w-]/g, '');
}

export function exportJson(result: AnalysisResult): void {
  const content = JSON.stringify(result, null, 2);
  downloadBlob(
    content,
    `hhparser_${slug(result.query)}.json`,
    'application/json',
  );
}

function toCsv(rows: CountItem[], header: [string, string]): string {
  const lines = [header.join(',')];
  for (const { label, count } of rows) {
    const escaped = label.includes(',')
      ? `"${label.replace(/"/g, '""')}"`
      : label;
    lines.push(`${escaped},${count}`);
  }
  return lines.join('\n');
}

export function exportCsv(result: AnalysisResult): void {
  downloadBlob(
    toCsv(result.hot_skills, ['skill', 'count']),
    `hhparser_${slug(result.query)}_skills.csv`,
    'text/csv',
  );
  downloadBlob(
    toCsv(result.hot_keywords, ['word', 'count']),
    `hhparser_${slug(result.query)}_keywords.csv`,
    'text/csv',
  );
}
