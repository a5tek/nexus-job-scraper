export interface User {
  id: string;
  email: string;
  name: string;
  is_active?: boolean;
}

export interface ListingItem {
  id: string;
  title: string;
  company: string;
  location: string | null;
  remote_ok: boolean | null;
  stipend: string | null;
  required_skills: string[];
  experience_level?: string | null;
  deadline: string | null;
  source_url: string | null;
  match_score?: number | null;
  match_explanation?: string | null;
  is_saved?: boolean;
}

export interface SavedListingItem {
  id?: string;
  saved_id?: string;
  user_id?: string;
  listing_id?: string;
  created_at?: string;
  saved_at?: string;
  notes?: string | null;
  listing: {
    id: string;
    title: string;
    company: string;
    location: string | null;
    remote_ok: boolean | null;
    stipend: string | null;
    required_skills: string[];
    experience_level?: string | null;
    deadline: string | null;
    source_url?: string | null;
    match_score?: number | null;
    match_explanation?: string | null;
    is_saved?: boolean;
  };
  match?: {
    display_score: number;
    justification: string;
  } | null;
}

export type ProcessingStatus =
  | "uploaded"
  | "reading"
  | "understanding"
  | "matching"
  | "ready"
  | "failed"
  | "none";

export interface ResumeStatusResponse {
  id: string;
  has_active_resume: boolean;
  file_name: string | null;
  processing_status: ProcessingStatus | null;
  error_message: string | null;
  matches_calculated?: number;
}

export interface ActiveResumeDetail {
  id: string;
  file_name: string;
  file_url: string;
  processing_status: string;
  is_active: boolean;
  extracted_text: string | null;
  created_at: string;
}

export interface ResumeStep {
  key: string;
  label: string;
}

export interface ToolCallRecord {
  tool_name: string;
  arguments: Record<string, unknown>;
  result_summary: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  tools_called?: ToolCallRecord[];
  suggested_follow_ups?: string[];
  created_at: string;
}

export interface AgentChatResponse {
  response: string;
  tools_called: ToolCallRecord[];
  suggested_follow_ups: string[];
}

export interface BriefingItem {
  rank: number;
  listing_id: string;
  title: string;
  company: string;
  location: string | null;
  match_score: number | null;
  deadline: string | null;
}

export interface BriefingRecord {
  id: string;
  user_id: string;
  status: "queued" | "processing" | "done" | "failed";
  script: string | null;
  media_url: string | null;
  provider: string | null;
  error_message: string | null;
  completed_at: string | null;
  created_at: string;
  listings: BriefingItem[];
}
