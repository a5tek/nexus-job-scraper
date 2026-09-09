"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { 
  Bookmark, 
  Trash2, 
  ExternalLink, 
  Clock, 
  Sparkles, 
  AlertTriangle, 
  MapPin, 
  ArrowRight,
  Compass
} from "lucide-react";
import { apiClient } from "@/lib/api";

interface SavedListingItem {
  saved_id: string;
  saved_at: string;
  notes: string | null;
  listing: {
    id: string;
    title: string;
    company: string;
    location: string | null;
    remote_ok: boolean | null;
    stipend: string | null;
    required_skills: string[];
    deadline: string | null;
    source_url: string;
  };
  match?: {
    display_score: number;
    justification: string;
  } | null;
}

export default function ShortlistPage() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery<{ count: number; items: SavedListingItem[] }>({
    queryKey: ["shortlist"],
    queryFn: async () => apiClient("/shortlist"),
  });

  const removeMutation = useMutation({
    mutationFn: async (listingId: string) => {
      await apiClient(`/shortlist/${listingId}`, { method: "DELETE" });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["shortlist"] });
      queryClient.invalidateQueries({ queryKey: ["listings"] });
    },
  });

  const calculateDaysRemaining = (deadlineStr: string | null): number | null => {
    if (!deadlineStr) return null;
    const deadline = new Date(deadlineStr);
    const today = new Date();
    const diffTime = deadline.getTime() - today.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const urgentRoles = data?.items.filter((item) => {
    const days = calculateDaysRemaining(item.listing.deadline);
    return days !== null && days <= 7 && days >= 0;
  });

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-canvas py-8 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-pill bg-white border border-softBorder text-xs font-semibold text-secondaryText mb-2 shadow-2xs">
              <Bookmark className="w-3.5 h-3.5 text-accentBlue" />
              <span>Priority Tracking</span>
            </div>
            <h1 className="font-display text-3xl font-bold tracking-tight text-primaryText">
              Saved Shortlist
            </h1>
            <p className="text-sm text-secondaryText mt-1">
              Curated opportunities with approaching deadlines and semantic match profiles.
            </p>
          </div>

          <Link
            href="/discover"
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-btn bg-surface hover:bg-canvas border border-softBorder text-xs font-semibold text-primaryText transition-colors shadow-2xs"
          >
            <Compass className="w-3.5 h-3.5 text-accentBlue" />
            <span>Discover more roles</span>
          </Link>
        </div>

        {/* Urgent Deadlines Alert */}
        {urgentRoles && urgentRoles.length > 0 && (
          <div className="p-5 rounded-card bg-amber-50/80 border border-amber-200/80 shadow-2xs flex items-start space-x-4">
            <div className="w-9 h-9 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center shrink-0">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <h3 className="font-semibold text-sm text-amber-900">
                {urgentRoles.length} {urgentRoles.length === 1 ? "role is" : "roles are"} closing within 7 days!
              </h3>
              <p className="text-xs text-amber-800/90 leading-relaxed">
                Prioritize your application materials for:{" "}
                <span className="font-semibold">
                  {urgentRoles.map((r) => r.listing.title).join(", ")}
                </span>
                .
              </p>
            </div>
          </div>
        )}

        {/* Shortlist Content */}
        {isLoading ? (
          <div className="py-16 text-center space-y-3">
            <div className="w-8 h-8 mx-auto rounded-full border-2 border-accentBlue border-t-transparent animate-spin"></div>
            <p className="text-xs text-secondaryText font-medium">Loading your shortlisted opportunities...</p>
          </div>
        ) : error ? (
          <div className="p-6 bg-surface rounded-card border border-accentRed/30 text-center space-y-2">
            <p className="text-sm font-semibold text-accentRed">Failed to load shortlist</p>
            <p className="text-xs text-secondaryText">Please ensure you are signed in.</p>
          </div>
        ) : data && data.items.length === 0 ? (
          <div className="py-16 text-center bg-surface rounded-card border border-softBorder p-8 space-y-4">
            <div className="w-12 h-12 mx-auto rounded-2xl bg-canvas flex items-center justify-center text-secondaryText">
              <Bookmark className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="font-semibold text-base text-primaryText">Your shortlist is empty</h3>
              <p className="text-xs text-secondaryText max-w-sm mx-auto">
                Explore the Discover feed to bookmark exciting roles and track deadlines.
              </p>
            </div>
            <Link
              href="/discover"
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white text-xs font-semibold shadow-xs transition-all"
            >
              <span>Explore Discover Feed</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        ) : (
          <div className="grid gap-4">
            {data?.items.map((item) => {
              const daysRemaining = calculateDaysRemaining(item.listing.deadline);
              const isClosingSoon = daysRemaining !== null && daysRemaining <= 7 && daysRemaining >= 0;
              const matchScore = item.match?.display_score;

              return (
                <div
                  key={item.saved_id}
                  className="bg-surface rounded-card p-6 border border-softBorder shadow-2xs space-y-4 flex flex-col md:flex-row md:items-center justify-between gap-6"
                >
                  <div className="space-y-2 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      {matchScore ? (
                        <div
                          className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-pill text-xs font-bold ${
                            matchScore >= 80
                              ? "bg-accentGreen-subtle text-accentGreen border border-accentGreen/30"
                              : "bg-accentBlue-subtle text-accentBlue border border-accentBlue/30"
                          }`}
                        >
                          <Sparkles className="w-3 h-3" />
                          <span>{matchScore}% Fit</span>
                        </div>
                      ) : null}

                      {isClosingSoon && (
                        <div className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-pill text-xs font-bold bg-accentYellow-subtle text-amber-700 border border-amber-300">
                          <Clock className="w-3 h-3" />
                          <span>Closing in {daysRemaining} days</span>
                        </div>
                      )}
                    </div>

                    <h2 className="text-lg font-bold text-primaryText tracking-tight">
                      {item.listing.title}
                    </h2>

                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-secondaryText font-medium">
                      <span className="font-semibold text-primaryText">{item.listing.company}</span>
                      <span className="flex items-center space-x-1">
                        <MapPin className="w-3 h-3" />
                        <span>{item.listing.location || (item.listing.remote_ok ? "Remote" : "Not specified")}</span>
                      </span>
                      {item.listing.deadline && (
                        <span className="flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span>Deadline: {item.listing.deadline}</span>
                        </span>
                      )}
                    </div>

                    {item.match?.justification && (
                      <p className="text-xs text-secondaryText leading-relaxed pt-1 line-clamp-2">
                        {item.match.justification}
                      </p>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-3 shrink-0">
                    <a
                      href={item.listing.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="px-4 py-2.5 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white text-xs font-semibold shadow-2xs transition-all flex items-center space-x-1.5"
                    >
                      <span>Apply on Source</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>

                    <button
                      onClick={() => removeMutation.mutate(item.listing.id)}
                      title="Remove from shortlist"
                      className="p-2.5 rounded-btn bg-surface hover:bg-accentRed-subtle text-secondaryText hover:text-accentRed border border-softBorder hover:border-accentRed/30 transition-all"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
