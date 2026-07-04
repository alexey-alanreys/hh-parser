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

function toCsv(
  rows: CountItem[],
  hot: Set<string>,
  header: [string, string, string],
): string {
  const lines = [header.join(',')];
  for (const { label, count } of rows) {
    const escaped = label.includes(',')
      ? `"${label.replace(/"/g, '""')}"`
      : label;
    lines.push(`${escaped},${count},${hot.has(label)}`);
  }
  return lines.join('\n');
}

export function exportCsv(result: AnalysisResult): void {
  const hotSkills = new Set(result.hot_skills.map((s) => s.label));
  const hotKeywords = new Set(result.hot_keywords.map((k) => k.label));

  downloadBlob(
    toCsv(result.all_skills, hotSkills, ['skill', 'count', 'hot']),
    `hhparser_${slug(result.query)}_skills.csv`,
    'text/csv',
  );
  downloadBlob(
    toCsv(result.all_keywords, hotKeywords, ['word', 'count', 'hot']),
    `hhparser_${slug(result.query)}_keywords.csv`,
    'text/csv',
  );
}
