"use client";

import { useState } from "react";
import {
  UploadCloud,
  CheckCircle2,
  AlertCircle,
  FileText,
  Sparkles,
  RefreshCw,
  X,
} from "lucide-react";

interface UploadDropzoneProps {
  selectedFile: File | null;
  onSelectFile: (file: File | null) => void;
  onUpload: (file: File) => void;
  isUploading: boolean;
  hasActiveResume: boolean;
  uploadSuccess: string | null;
  uploadError: string | null;
  onClearMessages?: () => void;
}

export function UploadDropzone({
  selectedFile,
  onSelectFile,
  onUpload,
  isUploading,
  hasActiveResume,
  uploadSuccess,
  uploadError,
  onClearMessages,
}: UploadDropzoneProps) {
  const [dragOver, setDragOver] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const validateAndSetFile = (file: File) => {
    setLocalError(null);
    if (onClearMessages) onClearMessages();

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setLocalError("Please select a valid PDF document (.pdf extension).");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setLocalError("File size exceeds 10MB limit. Please upload a smaller PDF.");
      return;
    }

    onSelectFile(file);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const activeError = localError || uploadError;

  return (
    <div className="bg-surface rounded-card p-8 border border-softBorder shadow-2xs space-y-6">
      <div className="space-y-1">
        <h3 className="font-semibold text-base text-primaryText">
          {hasActiveResume ? "Upload New Resume Version" : "Upload Your Resume"}
        </h3>
        <p className="text-xs text-secondaryText">
          Nexus extracts your work history, skills, and projects using AI to accurately match you with open roles.
        </p>
      </div>

      {uploadSuccess && (
        <div className="p-3.5 rounded-btn bg-accentGreen-subtle border border-accentGreen/30 text-accentGreen text-xs flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span className="flex-1">{uploadSuccess}</span>
        </div>
      )}

      {activeError && (
        <div className="p-3.5 rounded-btn bg-accentRed-subtle border border-accentRed/30 text-accentRed text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span className="flex-1">{activeError}</span>
        </div>
      )}

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-card p-8 text-center transition-all flex flex-col items-center justify-center space-y-3 ${
          dragOver
            ? "border-accentBlue bg-accentBlue-subtle/30"
            : "border-softBorder hover:border-accentBlue/60 bg-canvas/40"
        }`}
      >
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
            <FileText className="w-5 h-5 text-accentBlue shrink-0" />
            <span className="text-xs font-semibold text-primaryText truncate max-w-[200px] sm:max-w-xs">
              {selectedFile.name}
            </span>
            <button
              type="button"
              onClick={() => onSelectFile(null)}
              className="text-secondaryText hover:text-accentRed p-1"
              title="Remove file"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <button
            onClick={() => onUpload(selectedFile)}
            disabled={isUploading}
            className="px-5 py-2 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white text-xs font-semibold shadow-xs transition-all flex items-center space-x-2 disabled:opacity-60 shrink-0"
          >
            {isUploading ? (
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
  );
}
