"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  Headphones, 
  Sparkles, 
  Play, 
  Pause,
  Square,
  Volume2,
  Clock, 
  Calendar, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle,
  FileText,
  MapPin,
  ExternalLink
} from "lucide-react";
import { apiClient } from "@/lib/api";
import type { BriefingRecord } from "@/types";

export default function BriefingsPage() {
  const queryClient = useQueryClient();
  const [selectedBriefingId, setSelectedBriefingId] = useState<string | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  // 1. Fetch user's briefings
  const { data: briefings, isLoading, error } = useQuery<BriefingRecord[]>({
    queryKey: ["briefings"],
    queryFn: async () => apiClient("/briefings"),
  });

  // 2. Generate new briefing mutation
  const generateMutation = useMutation({
    mutationFn: async () => {
      return apiClient<BriefingRecord>("/briefings", { method: "POST" });
    },
    onSuccess: (newBriefing) => {
      queryClient.invalidateQueries({ queryKey: ["briefings"] });
      setSelectedBriefingId(newBriefing.id);
    },
  });

  // Active briefing is either selected one or the latest one
  const activeBriefing = briefings && briefings.length > 0
    ? (briefings.find((b) => b.id === selectedBriefingId) || briefings[0])
    : null;

  // Cleanup speech synthesis on unmount or briefing switch
  useEffect(() => {
    return () => {
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, [selectedBriefingId]);

  const handleToggleSpeech = (text: string) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;

    if (isSpeaking && !isPaused) {
      window.speechSynthesis.pause();
      setIsPaused(true);
      return;
    }

    if (isSpeaking && isPaused) {
      window.speechSynthesis.resume();
      setIsPaused(false);
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    utterance.onend = () => {
      setIsSpeaking(false);
      setIsPaused(false);
    };

    utterance.onerror = () => {
      setIsSpeaking(false);
      setIsPaused(false);
    };

    window.speechSynthesis.speak(utterance);
    setIsSpeaking(true);
    setIsPaused(false);
  };

  const handleStopSpeech = () => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
    setIsPaused(false);
  };

  const getAudioUrl = (mediaUrl: string | null | undefined, briefingId: string): string => {
    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    if (!mediaUrl || mediaUrl.includes("cdn.nexus.internal")) {
      return `${apiBase}/briefings/${briefingId}/audio`;
    }
    if (mediaUrl.startsWith("http")) {
      return mediaUrl;
    }
    if (mediaUrl.startsWith("/api/v1")) {
      return `${apiBase.replace(/\/api\/v1\/?$/, "")}${mediaUrl}`;
    }
    return `${apiBase}${mediaUrl.startsWith("/") ? "" : "/"}${mediaUrl}`;
  };

  const audioUrl = activeBriefing ? getAudioUrl(activeBriefing.media_url, activeBriefing.id) : "";

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-canvas py-8 px-4 sm:px-6">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-pill bg-surface border border-softBorder text-xs font-semibold text-secondaryText mb-2 shadow-2xs">
              <Headphones className="w-3.5 h-3.5 text-accentYellow" />
              <span>Weekly Executive Digest</span>
            </div>
            <h1 className="font-display text-3xl font-bold tracking-tight text-primaryText">
              Executive Briefings
            </h1>
            <p className="text-sm text-secondaryText mt-1">
              Personalized audio digest synthesizing your top 3 matching opportunities.
            </p>
          </div>

          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="px-5 py-2.5 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white text-xs font-semibold shadow-xs transition-all flex items-center space-x-2 shrink-0 disabled:opacity-60"
          >
            <Sparkles className={`w-3.5 h-3.5 ${generateMutation.isPending ? "animate-spin" : ""}`} />
            <span>{generateMutation.isPending ? "Synthesizing Briefing..." : "Generate My Briefing"}</span>
          </button>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="py-16 text-center space-y-3">
            <div className="w-8 h-8 mx-auto rounded-full border-2 border-accentBlue border-t-transparent animate-spin"></div>
            <p className="text-xs text-secondaryText font-medium">Loading executive briefings...</p>
          </div>
        ) : error ? (
          <div className="p-6 bg-surface rounded-card border border-accentRed/30 text-center space-y-2">
            <p className="text-sm font-semibold text-accentRed">Failed to load briefings</p>
            <p className="text-xs text-secondaryText">Please make sure you are logged in.</p>
          </div>
        ) : !activeBriefing ? (
          <div className="py-16 text-center bg-surface rounded-card border border-softBorder p-8 space-y-4">
            <div className="w-12 h-12 mx-auto rounded-2xl bg-canvas flex items-center justify-center text-secondaryText">
              <Headphones className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="font-semibold text-base text-primaryText">No briefings generated yet</h3>
              <p className="text-xs text-secondaryText max-w-sm mx-auto">
                Generate your first 60-90 second personalized audio digest tailored to your active resume profile.
              </p>
            </div>
            <button
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending}
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white text-xs font-semibold shadow-xs transition-all"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Generate My Briefing Now</span>
            </button>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Featured Briefing Player Card */}
            <div className="bg-surface rounded-card p-6 md:p-8 border border-softBorder shadow-2xs space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-softBorder/60">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-2xl bg-accentYellow-subtle text-amber-800 flex items-center justify-center">
                    <Headphones className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="font-bold text-base text-primaryText">
                      Nexus Career Briefing
                    </h2>
                    <p className="text-xs text-secondaryText flex items-center space-x-2">
                      <span>Generated {new Date(activeBriefing.created_at).toLocaleDateString()}</span>
                      <span>·</span>
                      <span className="capitalize font-medium text-accentGreen flex items-center space-x-1">
                        <CheckCircle2 className="w-3 h-3" />
                        <span>{activeBriefing.status}</span>
                      </span>
                    </p>
                  </div>
                </div>

                {audioUrl && (
                  <a
                    href={audioUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3.5 py-1.5 rounded-btn bg-canvas hover:bg-softBorder/40 border border-softBorder text-xs font-semibold text-secondaryText hover:text-primaryText transition-colors flex items-center space-x-1.5"
                  >
                    <span>Download Audio</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>

              {/* Interactive AI Voice Narration */}
              {activeBriefing.script && (
                <div className="p-4 rounded-card bg-accentBlue/5 border border-accentBlue/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <Volume2 className="w-4 h-4 text-accentBlue" />
                      <h3 className="text-xs font-bold text-primaryText">
                        AI Executive Briefing Narration
                      </h3>
                      {isSpeaking && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-pill text-[10px] font-bold bg-accentGreen-subtle text-accentGreen border border-accentGreen/30 animate-pulse">
                          {isPaused ? "Paused" : "Playing"}
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-secondaryText">
                      Listen to your personalized digest read aloud with natural AI speech synthesis.
                    </p>
                  </div>

                  <div className="flex items-center space-x-2 shrink-0">
                    <button
                      onClick={() => handleToggleSpeech(activeBriefing.script || "")}
                      className="px-4 py-2 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white text-xs font-semibold shadow-2xs transition-all flex items-center space-x-1.5"
                    >
                      {isSpeaking && !isPaused ? (
                        <>
                          <Pause className="w-3.5 h-3.5" />
                          <span>Pause Narration</span>
                        </>
                      ) : (
                        <>
                          <Play className="w-3.5 h-3.5" />
                          <span>{isPaused ? "Resume Narration" : "Listen to Briefing"}</span>
                        </>
                      )}
                    </button>

                    {isSpeaking && (
                      <button
                        onClick={handleStopSpeech}
                        title="Stop Narration"
                        className="p-2 rounded-btn bg-surface hover:bg-canvas border border-softBorder text-secondaryText hover:text-accentRed transition-colors"
                      >
                        <Square className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Native Audio Stream Player */}
              {audioUrl && (
                <div className="p-4 rounded-card bg-canvas border border-softBorder space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-primaryText">
                    <span>Audio Stream</span>
                    <span className="text-secondaryText font-normal">Stereo 44.1kHz WAV</span>
                  </div>
                  <audio
                    controls
                    src={audioUrl}
                    className="w-full h-10 accent-accentBlue"
                  >
                    Your browser does not support the audio element.
                  </audio>
                </div>
              )}

              {/* Linked Opportunities (Top 3) */}
              <div className="space-y-3">
                <h3 className="font-semibold text-xs uppercase tracking-wider text-secondaryText">
                  Spotlighted Opportunities
                </h3>

                <div className="grid gap-3 sm:grid-cols-3">
                  {activeBriefing.listings.map((item) => (
                    <div
                      key={item.listing_id}
                      className="p-4 rounded-btn bg-canvas border border-softBorder space-y-2 relative"
                    >
                      <div className="flex items-center justify-between">
                        <span className="w-5 h-5 rounded-full bg-accentBlue text-white flex items-center justify-center font-bold text-[10px]">
                          #{item.rank}
                        </span>
                        {item.match_score && (
                          <span className="text-[11px] font-bold text-accentGreen">
                            {item.match_score}% Fit
                          </span>
                        )}
                      </div>

                      <h4 className="font-bold text-xs text-primaryText line-clamp-1">
                        {item.title}
                      </h4>
                      <p className="text-[11px] text-secondaryText font-medium">
                        {item.company}
                      </p>
                      {item.deadline && (
                        <p className="text-[10px] text-secondaryText flex items-center space-x-1">
                          <Clock className="w-2.5 h-2.5" />
                          <span>Due {item.deadline}</span>
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Script / Transcript */}
              {activeBriefing.script && (
                <div className="space-y-2 pt-2 border-t border-softBorder/60">
                  <h3 className="font-semibold text-xs uppercase tracking-wider text-secondaryText flex items-center space-x-1.5">
                    <FileText className="w-3.5 h-3.5" />
                    <span>Briefing Script & Transcript</span>
                  </h3>
                  <div className="p-4 rounded-btn bg-canvas border border-softBorder text-xs text-primaryText leading-relaxed whitespace-pre-wrap font-normal">
                    {activeBriefing.script}
                  </div>
                </div>
              )}
            </div>

            {/* Previous Briefings Archive */}
            {briefings && briefings.length > 1 && (
              <div className="space-y-3">
                <h3 className="font-semibold text-sm text-primaryText">Briefing Archive</h3>
                <div className="grid gap-2">
                  {briefings.map((b) => (
                    <button
                      key={b.id}
                      onClick={() => setSelectedBriefingId(b.id)}
                      className={`w-full text-left p-4 rounded-btn border transition-all flex items-center justify-between ${
                        b.id === activeBriefing.id
                          ? "bg-surface border-accentBlue shadow-2xs"
                          : "bg-surface hover:bg-canvas border-softBorder"
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <Play className="w-4 h-4 text-accentBlue" />
                        <div>
                          <h4 className="text-xs font-semibold text-primaryText">
                            Briefing from {new Date(b.created_at).toLocaleDateString()}
                          </h4>
                          <p className="text-[11px] text-secondaryText">
                            {b.listings.length} spotlighted opportunities · Status: {b.status}
                          </p>
                        </div>
                      </div>
                      <span className="text-xs font-semibold text-accentBlue">Listen</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
