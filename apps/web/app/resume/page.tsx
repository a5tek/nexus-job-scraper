"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  FileText, 
  UploadCloud, 
  CheckCircle2, 
  Clock, 
  RefreshCw, 
  Sparkles, 
  AlertCircle,
  FileCheck,
  ChevronDown,
  ChevronUp,
  LogIn,
  ArrowRight,
  ShieldCheck
} from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

interface ResumeStatusResponse {
  id: string;
  has_active_resume: boolean;
  file_name: string | null;
  processing_status: string | null;  // uploaded, reading, understanding, matching, ready, failed
  error_message: string | null;
  matches_calculated?: number;
}

interface ActiveResumeDetail {
  id: string;
  file_name: string;
  file_url: string;
  processing_status: string;
  is_active: boolean;
  extracted_text: string | null;
  created_at: string;
}

export default function ResumePage() {
  const queryClient = useQueryClient();
  const { user, token, isLoading: authLoading } = useAuth();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showExtractedText, setShowExtractedText] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  // 1. Fetch active resume status (only if logged in)
  const { data: statusData, isLoading: statusLoading } = useQuery<ResumeStatusResponse>({
    queryKey: ["resume-status"],
    queryFn: async () => apiClient("/resume/status"),
    enabled: !!user,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data && data.processing_status && ["uploaded", "reading", "understanding", "matching"].includes(data.processing_status)) {
        return 2000;
      }
      return false;
    },
  });

  // 2. Fetch full resume detail if exists
  const { data: resumeDetail } = useQuery<ActiveResumeDetail | null>({
    queryKey: ["resume-detail"],
    queryFn: async () => {
      try {
        return await apiClient<ActiveResumeDetail>("/resume");
      } catch {
        return null;
      }
    },
    enabled: !!user && !!statusData?.has_active_resume,
  });

  // Upload Mutation
  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      setUploadError(null);
      setUploadSuccess(null);

      const activeToken = token || (typeof window !== "undefined" ? localStorage.getItem("nexus_token") : null);
      if (!activeToken) {
        throw new Error("You must be signed in to upload a resume. Please sign in or create an account.");
      }

      const formData = new FormData();
      formData.append("file", file);

      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

      const res = await fetch(`${API_BASE}/resume/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${activeToken}`,
        },
        body: formData,
      });

      if (!res.ok) {
        let errData: any = {};
        try {
          errData = await res.json();
        } catch {}
        const msg = errData?.error?.message || errData?.detail || "Failed to upload resume.";
        throw new Error(msg);
      }

      return res.json();
    },
    onSuccess: (data) => {
      setSelectedFile(null);
      setUploadSuccess("Resume successfully parsed, embedded, and matched against active opportunities!");
      queryClient.invalidateQueries({ queryKey: ["resume-status"] });
      queryClient.invalidateQueries({ queryKey: ["resume-detail"] });
      queryClient.invalidateQueries({ queryKey: ["listings"] });
    },
    onError: (err: any) => {
      setUploadError(err.message || "Upload failed. Please ensure you are logged in.");
    },
  });

  // Re-match Mutation
  const rematchMutation = useMutation({
    mutationFn: async () => {
      return apiClient("/resume/match", { method: "POST" });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resume-status"] });
      queryClient.invalidateQueries({ queryKey: ["listings"] });
      queryClient.invalidateQueries({ queryKey: ["shortlist"] });
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!file.name.toLowerCase().endsWith(".pdf")) {
        setUploadError("Please select a PDF document (.pdf extension).");
        return;
      }
      setSelectedFile(file);
      setUploadError(null);
      setUploadSuccess(null);
    }
  };

  const steps = [
    { key: "uploaded", label: "Uploaded" },
    { key: "reading", label: "Text Extraction" },
    { key: "understanding", label: "Semantic Embedding" },
    { key: "matching", label: "Opportunity Matching" },
    { key: "ready", label: "Ready & Scored" },
  ];

  const currentStatus = statusData?.processing_status || "none";
  const getStepIndex = (status: string) => {
    const idx = steps.findIndex((s) => s.key === status);
    return idx === -1 ? 0 : idx;
  };
  const activeStepIdx = getStepIndex(currentStatus);

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-canvas py-8 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-pill bg-white border border-softBorder text-xs font-semibold text-secondaryText mb-2 shadow-2xs">
            <Sparkles className="w-3.5 h-3.5 text-accentGreen" />
            <span>Semantic Resume Engine</span>
          </div>
          <h1 className="font-display text-3xl font-bold tracking-tight text-primaryText">
            Resume Intelligence
          </h1>
          <p className="text-sm text-secondaryText mt-1">
            Upload your resume to extract competencies, project vector embeddings, and rank opportunities.
          </p>
        </div>

        {/* Authentication Notice if logged out */}
        {!authLoading && !user && (
          <div className="bg-surface rounded-card p-6 border border-accentBlue/30 shadow-2xs space-y-4">
            <div className="flex items-start space-x-3.5">
              <div className="w-10 h-10 rounded-xl bg-accentBlue-subtle text-accentBlue flex items-center justify-center shrink-0">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div className="space-y-1">
                <h3 className="font-bold text-sm text-primaryText">
                  Candidate Account Required for Resume Processing
                </h3>
                <p className="text-xs text-secondaryText leading-relaxed">
                  To securely isolate your parsed career profile, vector embeddings, and personalized match justifications, you must be signed in.
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3 pt-1">
              <Link
                href="/login"
                className="px-4 py-2 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white text-xs font-semibold shadow-2xs transition-all flex items-center space-x-1.5"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Sign In to Upload</span>
              </Link>
              <Link
                href="/signup"
                className="px-4 py-2 rounded-btn bg-canvas hover:bg-softBorder/40 border border-softBorder text-xs font-semibold text-primaryText transition-colors"
              >
                <span>Create Account</span>
              </Link>
            </div>
          </div>
        )}

        {/* Status Stepper Card */}
        {user && statusData?.has_active_resume && (
          <div className="bg-surface rounded-card p-6 border border-softBorder shadow-2xs space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-accentGreen-subtle text-accentGreen flex items-center justify-center">
                  <FileCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-semibold text-sm text-primaryText">
                    Active Resume: {statusData.file_name}
                  </h3>
                  <p className="text-xs text-secondaryText">
                    Status: <span className="capitalize font-medium text-primaryText">{currentStatus}</span>
                    {statusData.matches_calculated !== undefined && (
                      <span className="ml-2 font-medium text-accentGreen">
                        · {statusData.matches_calculated} opportunities scored
                      </span>
                    )}
                  </p>
                </div>
              </div>

              <button
                onClick={() => rematchMutation.mutate()}
                disabled={rematchMutation.isPending}
                className="px-3.5 py-1.5 rounded-btn bg-canvas hover:bg-softBorder/40 border border-softBorder text-xs font-semibold text-primaryText flex items-center space-x-1.5 transition-all disabled:opacity-60"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${rematchMutation.isPending ? "animate-spin" : ""}`} />
                <span>Re-calculate scores</span>
              </button>
            </div>

            {/* Stepper progress */}
            <div className="grid grid-cols-5 gap-2 pt-2">
              {steps.map((step, idx) => {
                const isCompleted = activeStepIdx >= idx || currentStatus === "ready";
                const isCurrent = activeStepIdx === idx && currentStatus !== "ready";

                return (
                  <div key={step.key} className="space-y-2 text-center">
                    <div
                      className={`h-2 rounded-pill transition-all ${
                        isCompleted
                          ? "bg-accentGreen"
                          : isCurrent
                          ? "bg-accentBlue animate-pulse"
                          : "bg-softBorder"
                      }`}
                    />
                    <span className="text-[11px] font-medium text-secondaryText block leading-tight">
                      {step.label}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Upload Dropzone */}
        <div className="bg-surface rounded-card p-8 border border-softBorder shadow-2xs space-y-6">
          <div className="space-y-1">
            <h3 className="font-semibold text-base text-primaryText">
              {statusData?.has_active_resume ? "Upload New Resume Version" : "Upload Your Resume"}
            </h3>
            <p className="text-xs text-secondaryText">
              Nexus parses PDF files using PyMuPDF and projects a normalized 384-dimensional vector embedding.
            </p>
          </div>

          {uploadSuccess && (
            <div className="p-3.5 rounded-btn bg-accentGreen-subtle border border-accentGreen/30 text-accentGreen text-xs flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{uploadSuccess}</span>
            </div>
          )}

          {uploadError && (
            <div className="p-3.5 rounded-btn bg-accentRed-subtle border border-accentRed/30 text-accentRed text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}

          <div className="border-2 border-dashed border-softBorder hover:border-accentBlue/60 rounded-card p-8 text-center bg-canvas/40 transition-all flex flex-col items-center justify-center space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-surface border border-softBorder flex items-center justify-center text-accentBlue shadow-2xs">
              <UploadCloud className="w-6 h-6" />
            </div>

            <div className="space-y-1">
              <p className="text-sm font-semibold text-primaryText">
                {selectedFile ? selectedFile.name : "Select or drag your PDF resume"}
              </p>
              <p className="text-xs text-secondaryText">Standard PDF document up to 10MB</p>
            </div>

            <label className="cursor-pointer px-4 py-2 rounded-btn bg-surface hover:bg-canvas border border-softBorder text-xs font-semibold text-primaryText shadow-2xs transition-colors">
              <span>Browse File</span>
              <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          </div>

          {selectedFile && (
            <div className="flex items-center justify-between p-4 rounded-btn bg-canvas border border-softBorder">
              <div className="flex items-center space-x-2.5">
                <FileText className="w-5 h-5 text-accentBlue" />
                <span className="text-xs font-semibold text-primaryText">{selectedFile.name}</span>
              </div>

              <button
                onClick={() => uploadMutation.mutate(selectedFile)}
                disabled={uploadMutation.isPending}
                className="px-5 py-2 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white text-xs font-semibold shadow-xs transition-all flex items-center space-x-2 disabled:opacity-60"
              >
                {uploadMutation.isPending ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Processing & Matching...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Upload & Match</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Extracted Text Preview Drawer */}
        {resumeDetail?.extracted_text && (
          <div className="bg-surface rounded-card p-6 border border-softBorder shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <h3 className="font-semibold text-sm text-primaryText">Extracted Profile Text</h3>
                <p className="text-xs text-secondaryText">Parsed text tokens utilized for embedding projection</p>
              </div>

              <button
                onClick={() => setShowExtractedText(!showExtractedText)}
                className="text-xs font-semibold text-accentBlue flex items-center space-x-1"
              >
                <span>{showExtractedText ? "Hide preview" : "View text"}</span>
                {showExtractedText ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>
            </div>

            {showExtractedText && (
              <pre className="p-4 rounded-btn bg-canvas border border-softBorder text-xs text-secondaryText overflow-x-auto whitespace-pre-wrap font-mono max-h-72">
                {resumeDetail.extracted_text}
              </pre>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
