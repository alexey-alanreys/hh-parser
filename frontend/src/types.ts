export type Experience =
  'noExperience' | 'between1And3' | 'between3And6' | 'moreThan6';

export interface ScanRequest {
  query: string;
  experience?: Experience | null;
  max_vacancies: number;
}

export interface CountItem {
  label: string;
  count: number;
}

export interface AnalysisResult {
  query: string;
  total_vacancies: number;
  hot_skills: CountItem[];
  hot_keywords: CountItem[];
  all_skills: CountItem[];
  all_keywords: CountItem[];
}

export type JobStatus = 'pending' | 'running' | 'done' | 'error';
export type JobStage = 'collecting' | 'enriching' | 'analyzing';

export interface JobProgress {
  stage: JobStage;
  current: number;
  total: number;
}

export interface JobStatusOut {
  job_id: string;
  status: JobStatus;
  progress: JobProgress | null;
  result: AnalysisResult | null;
  error: string | null;
}
