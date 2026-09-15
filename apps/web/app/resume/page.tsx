"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Sparkles, ShieldCheck, LogIn } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { UploadDropzone } from "@/components/resume/UploadDropzone";
import { ResumeStatus } from "@/components/resume/ResumeStatus";
import type {
  ResumeStatusResponse,
  ActiveResumeDetail,
  ResumeStep,
} from "@/types";

const steps: ResumeStep[] = [
  { key: "uploaded", label: "Uploaded" },
  { key: "reading", label: "Text Extraction" },
  { key: "understanding", label: "Semantic Embedding" },
  { key: "matching", label: "Opportunity Matching" },
  { key: "ready", label: "Ready & Scored" },
];

export default function ResumePage() {
  const queryClient = useQueryClient();
  const { user, isLoading: authLoading } = useAuth();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showExtractedText, setShowExtractedText] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  // 1. Fetch active resume status (only if logged in)
  const { data: statusData } = useQuery<ResumeStatusResponse>({
    queryKey: ["resume-status"],
    queryFn: async () => apiClient("/resume/status"),
    enabled: !!user,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (
        data &&
        data.processing_status &&
        ["uploaded", "reading", "understanding", "matching"].includes(
          data.processing_status
        )
      ) {
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

      if (!user) {
        throw new Error(
          "You must be signed in to upload a resume. Please sign in or create an account."
        );
      }

      const formData = new FormData();
      formData.append("file", file);

      return await apiClient<ActiveResumeDetail>("/resume/upload", {
        method: "POST",
        body: formData,
      });
    },
    onSuccess: () => {
      setSelectedFile(null);
      setUploadSuccess(
        "Resume successfully parsed, embedded, and matched against active opportunities!"
      );
      queryClient.invalidateQueries({ queryKey: ["resume-status"] });
      queryClient.invalidateQueries({ queryKey: ["resume-detail"] });
      queryClient.invalidateQueries({ queryKey: ["listings"] });
    },
    onError: (err: unknown) => {
      const message =
        err instanceof Error
          ? err.message
          : "Upload failed. Please ensure you are logged in.";
      setUploadError(message);
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
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-pill bg-surface border border-softBorder text-xs font-semibold text-secondaryText mb-2 shadow-2xs">
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

        {/* Status Stepper Subcomponent */}
        {user && statusData?.has_active_resume && (
          <ResumeStatus
            statusData={statusData}
            currentStatus={currentStatus}
            steps={steps}
            activeStepIdx={activeStepIdx}
            onRematch={() => rematchMutation.mutate()}
            isRematching={rematchMutation.isPending}
            resumeDetail={resumeDetail ?? null}
            showExtractedText={showExtractedText}
            onToggleExtractedText={() =>
              setShowExtractedText(!showExtractedText)
            }
          />
        )}

        {/* Upload Dropzone Subcomponent */}
        <UploadDropzone
          selectedFile={selectedFile}
          onSelectFile={setSelectedFile}
          onUpload={(file) => uploadMutation.mutate(file)}
          isUploading={uploadMutation.isPending}
          hasActiveResume={!!statusData?.has_active_resume}
          uploadSuccess={uploadSuccess}
          uploadError={uploadError}
          onClearMessages={() => {
            setUploadError(null);
            setUploadSuccess(null);
          }}
        />
      </div>
    </div>
  );
}
