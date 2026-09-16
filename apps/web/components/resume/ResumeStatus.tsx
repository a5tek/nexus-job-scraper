"use client";

import {
  FileCheck,
  RefreshCw,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import type {
  ResumeStatusResponse,
  ActiveResumeDetail,
  ResumeStep,
} from "@/types";

interface ResumeStatusProps {
  statusData: ResumeStatusResponse;
  currentStatus: string;
  steps: ResumeStep[];
  activeStepIdx: number;
  onRematch: () => void;
  isRematching: boolean;
  resumeDetail: ActiveResumeDetail | null;
  showExtractedText: boolean;
  onToggleExtractedText: () => void;
}

export function ResumeStatus({
  statusData,
  currentStatus,
  steps,
  activeStepIdx,
  onRematch,
  isRematching,
  resumeDetail,
  showExtractedText,
  onToggleExtractedText,
}: ResumeStatusProps) {
  return (
    <div className="space-y-6">
      {/* Status Stepper Card */}
      <div className="bg-surface rounded-card p-6 border border-softBorder shadow-2xs space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-accentGreen-subtle text-accentGreen flex items-center justify-center shrink-0">
              <FileCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-sm text-primaryText">
                Active Resume: {statusData.file_name}
              </h3>
              <p className="text-xs text-secondaryText">
                Status:{" "}
                <span className="capitalize font-medium text-primaryText">
                  {currentStatus}
                </span>
                {statusData.matches_calculated !== undefined && (
                  <span className="ml-2 font-medium text-accentGreen">
                    · {statusData.matches_calculated} opportunities scored
                  </span>
                )}
              </p>
            </div>
          </div>

          <button
            onClick={onRematch}
            disabled={isRematching}
            className="px-3.5 py-1.5 rounded-btn bg-canvas hover:bg-softBorder/40 border border-softBorder text-xs font-semibold text-primaryText flex items-center space-x-1.5 transition-all disabled:opacity-60"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${isRematching ? "animate-spin" : ""}`}
            />
            <span>Re-calculate scores</span>
          </button>
        </div>

        {/* Stepper progress */}
        <div className="grid grid-cols-5 gap-2 pt-2">
          {steps.map((step, idx) => {
            const isCompleted =
              activeStepIdx >= idx || currentStatus === "ready";
            const isCurrent =
              activeStepIdx === idx && currentStatus !== "ready";

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

      {/* Extracted Text Preview Drawer */}
      {resumeDetail?.extracted_text && (
        <div className="bg-surface rounded-card p-6 border border-softBorder shadow-2xs space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <h3 className="font-semibold text-sm text-primaryText">
                Extracted Profile Text
              </h3>
              <p className="text-xs text-secondaryText">
                Extracted text used by AI to analyze your skills and background
              </p>
            </div>

            <button
              onClick={onToggleExtractedText}
              className="text-xs font-semibold text-accentBlue flex items-center space-x-1"
            >
              <span>{showExtractedText ? "Hide preview" : "View text"}</span>
              {showExtractedText ? (
                <ChevronUp className="w-3.5 h-3.5" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5" />
              )}
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
  );
}
