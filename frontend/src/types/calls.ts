export type CallStatus = "in_progress" | "success" | "failed";

export interface Call {
  id: string;
  phone_number: string;
  caller_name: string | null;
  duration_seconds: number | null;
  status: CallStatus;
  summary: string | null;
  label: string | null;
  started_at: string;
  ended_at: string | null;
  created_at: string;
  updated_at: string;
  raw_transcript: string | null;
  notes: string | null;
}

export interface CallCounts {
  in_progress: number;
  success: number;
  failed: number;
}

export interface PaginatedCallsResponse {
  data: Call[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  counts: CallCounts;
}

export type SortByField =
  | "phone_number"
  | "caller_name"
  | "status"
  | "label"
  | "duration_seconds"
  | "started_at";

export type SortOrder = "asc" | "desc";

export const CALL_LABELS = [
  "Sales inquiry",
  "Support",
  "Complaint",
  "Appointment",
  "Follow-up",
  "Other",
] as const;

export type CallLabel = (typeof CALL_LABELS)[number];

export type FilterType =
  | "caller_name"
  | "phone_number"
  | "label"
  | "min_duration"
  | "max_duration";

export interface CallsQueryParams {
  status?: CallStatus;
  caller_name?: string;
  phone_number?: string;
  label?: string;
  min_duration?: number;
  max_duration?: number;
  sort_by?: SortByField;
  sort_order?: SortOrder;
  page?: number;
  page_size?: number;
}
