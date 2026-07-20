/** Auto-generated PPIE SDK stubs — regenerate via platform.sdk.generate */
export interface DogProfileInput {
  name: string;
  primary_breed: string;
  secondary_breed?: string | null;
  breed_split_pct?: number;
  age_years: number;
  weight_kg: number;
  current_environment: string;
  activity_level?: string;
  sex?: string | null;
  observed_conditions?: string[];
}

export type ClinicalReportResponse = {
  analyze: Record<string, unknown>;
  assessment: Record<string, unknown>;
  report: Record<string, unknown>;
  reportModels: Record<string, unknown>;
  clinicalReport: Record<string, unknown>;
  trace?: Record<string, unknown>;
};
