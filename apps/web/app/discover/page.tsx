"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  Search, 
  Bookmark, 
  ExternalLink, 
  Sparkles, 
  MapPin, 
  DollarSign, 
  Clock, 
  CheckCircle2, 
  ChevronDown, 
  ChevronUp,
  Globe,
  SlidersHorizontal
} from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

interface MatchDetail {
  score: number;
  display_score: number;
  justification: string;
  strengths: string[];
  gaps: string[];
}

interface ListingItem {
  id: string;
  title: string;
  company: string;
  location: string | null;
  remote_ok: boolean | null;
  stipend: string | null;
  required_skills: string[];
  experience_level: string | null;
  deadline: string | null;
  source_url: string;
  created_at: string;
  is_saved?: boolean;
  match?: MatchDetail | null;
}

interface ListingsResponse {
  total: number;
  limit: number;
  offset: number;
  items: ListingItem[];
}

export default function DiscoverPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [searchQuery, setSearchQuery] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [minFit, setMinFit] = useState<number | null>(null);
  const [expandedMatchId, setExpandedMatchId] = useState<string | null>(null);

  // Fetch opportunity listings
  const { data, isLoading, error } = useQuery<ListingsResponse>({
    queryKey: ["listings", remoteOnly, minFit],
    queryFn: async () => {
      let endpoint = `/listings?limit=30`;
      if (remoteOnly) endpoint += `&remote_only=true`;
      if (minFit) endpoint += `&min_fit=${minFit}`;
      return apiClient<ListingsResponse>(endpoint);
    },
  });

  // Toggle Shortlist mutation
  const toggleSaveMutation = useMutation({
    mutationFn: async ({ listingId, isSaved }: { listingId: string; isSaved: boolean }) => {
      if (isSaved) {
        await apiClient(`/shortlist/${listingId}`, { method: "DELETE" });
      } else {
        await apiClient(`/shortlist/${listingId}`, { method: "POST" });
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["listings"] });
      queryClient.invalidateQueries({ queryKey: ["shortlist"] });
    },
  });

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      queryClient.invalidateQueries({ queryKey: ["listings"] });
      return;
    }

    try {
      const searchRes = await apiClient<{ count: number; items: ListingItem[] }>(
        "/listings/search",
        {
          method: "POST",
          body: JSON.stringify({
            query: searchQuery,
            limit: 25,
            remote_only: remoteOnly,
          }),
        }
      );
      queryClient.setQueryData(["listings", remoteOnly, minFit], {
        total: searchRes.count,
        limit: 25,
        offset: 0,
        items: searchRes.items,
      });
    } catch {
      // Fallback
    }
  };

  const calculateDaysRemaining = (deadlineStr: string | null): number | null => {
    if (!deadlineStr) return null;
    const deadline = new Date(deadlineStr);
    const today = new Date();
    const diffTime = deadline.getTime() - today.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-canvas py-8 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-pill bg-white border border-softBorder text-xs font-semibold text-secondaryText mb-2 shadow-2xs">
              <Sparkles className="w-3.5 h-3.5 text-accentBlue" />
              <span>Live Semantic Pipeline</span>
            </div>
            <h1 className="font-display text-3xl font-bold tracking-tight text-primaryText">
              Discover Opportunities
            </h1>
            <p className="text-sm text-secondaryText mt-1">
              Roles indexed across public ecosystems and scored against your active resume.
            </p>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="bg-surface rounded-card p-4 border border-softBorder shadow-xs space-y-4">
          <form onSubmit={handleSearch} className="flex gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-secondaryText absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search semantic concepts (e.g., 'distributed systems Golang', 'AI agents Python')..."
                className="w-full pl-10 pr-4 py-2.5 rounded-btn bg-canvas border border-softBorder text-sm text-primaryText placeholder:text-secondaryText/60 focus:outline-none focus:ring-2 focus:ring-accentBlue/20 focus:border-accentBlue transition-all"
              />
            </div>
            <button
              type="submit"
              className="px-5 py-2.5 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white text-sm font-semibold shadow-xs transition-all flex items-center space-x-2 shrink-0"
            >
              <span>Search</span>
            </button>
          </form>

          {/* Filter Pills */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-softBorder/60 text-xs">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-secondaryText font-medium flex items-center space-x-1 mr-1">
                <SlidersHorizontal className="w-3 h-3" />
                <span>Filters:</span>
              </span>

              <button
                type="button"
                onClick={() => setRemoteOnly(!remoteOnly)}
                className={`px-3 py-1.5 rounded-pill font-medium transition-all flex items-center space-x-1.5 ${
                  remoteOnly
                    ? "bg-accentBlue text-white shadow-2xs"
                    : "bg-canvas border border-softBorder text-secondaryText hover:text-primaryText"
                }`}
              >
                <Globe className="w-3 h-3" />
                <span>Remote Only</span>
              </button>

              <button
                type="button"
                onClick={() => setMinFit(minFit === 75 ? null : 75)}
                className={`px-3 py-1.5 rounded-pill font-medium transition-all flex items-center space-x-1.5 ${
                  minFit === 75
                    ? "bg-accentGreen text-white shadow-2xs"
                    : "bg-canvas border border-softBorder text-secondaryText hover:text-primaryText"
                }`}
              >
                <CheckCircle2 className="w-3 h-3" />
                <span>High Fit (75%+)</span>
              </button>

              <button
                type="button"
                onClick={() => setMinFit(minFit === 90 ? null : 90)}
                className={`px-3 py-1.5 rounded-pill font-medium transition-all flex items-center space-x-1.5 ${
                  minFit === 90
                    ? "bg-accentGreen text-white shadow-2xs"
                    : "bg-canvas border border-softBorder text-secondaryText hover:text-primaryText"
                }`}
              >
                <Sparkles className="w-3 h-3" />
                <span>Elite Fit (90%+)</span>
              </button>
            </div>

            <div className="text-secondaryText font-medium">
              {data ? `${data.items.length} opportunities shown` : "Loading..."}
            </div>
          </div>
        </div>

        {/* Listings Feed */}
        {isLoading ? (
          <div className="py-16 text-center space-y-3">
            <div className="w-8 h-8 mx-auto rounded-full border-2 border-accentBlue border-t-transparent animate-spin"></div>
            <p className="text-xs text-secondaryText font-medium">Calculating semantic fits across opportunities...</p>
          </div>
        ) : error ? (
          <div className="p-6 bg-surface rounded-card border border-accentRed/30 text-center space-y-2">
            <p className="text-sm font-semibold text-accentRed">Unable to load opportunities</p>
            <p className="text-xs text-secondaryText">Ensure the backend API is running at localhost:8000.</p>
          </div>
        ) : data && data.items.length === 0 ? (
          <div className="py-16 text-center bg-surface rounded-card border border-softBorder p-8 space-y-3">
            <div className="w-12 h-12 mx-auto rounded-2xl bg-canvas flex items-center justify-center text-secondaryText">
              <Search className="w-6 h-6" />
            </div>
            <h3 className="font-semibold text-base text-primaryText">No matching roles found</h3>
            <p className="text-xs text-secondaryText max-w-md mx-auto">
              Try broadening your search query, removing the remote filter, or trigger the scraping pipeline from the internal portal.
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {data?.items.map((listing) => {
              const daysRemaining = calculateDaysRemaining(listing.deadline);
              const isClosingSoon = daysRemaining !== null && daysRemaining <= 7 && daysRemaining >= 0;
              const isExpanded = expandedMatchId === listing.id;
              const matchScore = listing.match?.display_score;

              return (
                <div
                  key={listing.id}
                  className="bg-surface rounded-card p-6 border border-softBorder hover:border-softBorder/80 transition-all shadow-2xs space-y-4"
                >
                  {/* Top row: match badge, title, save action */}
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1.5 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        {matchScore ? (
                          <div
                            className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-pill text-xs font-bold ${
                              matchScore >= 80
                                ? "bg-accentGreen-subtle text-accentGreen border border-accentGreen/30"
                                : matchScore >= 60
                                ? "bg-accentBlue-subtle text-accentBlue border border-accentBlue/30"
                                : "bg-canvas text-secondaryText border border-softBorder"
                            }`}
                          >
                            <Sparkles className="w-3 h-3" />
                            <span>{matchScore}% Fit</span>
                          </div>
                        ) : (
                          <div className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-pill text-xs font-medium bg-canvas text-secondaryText border border-softBorder">
                            <span>Unscored (Upload Resume)</span>
                          </div>
                        )}

                        {isClosingSoon && (
                          <div className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-pill text-xs font-bold bg-accentYellow-subtle text-amber-700 border border-amber-300">
                            <Clock className="w-3 h-3" />
                            <span>Closing in {daysRemaining} days</span>
                          </div>
                        )}
                      </div>

                      <h2 className="text-lg font-bold text-primaryText tracking-tight">
                        {listing.title}
                      </h2>

                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-secondaryText font-medium">
                        <span className="font-semibold text-primaryText">{listing.company}</span>
                        <span className="flex items-center space-x-1">
                          <MapPin className="w-3 h-3" />
                          <span>{listing.location || (listing.remote_ok ? "Remote" : "Not specified")}</span>
                        </span>
                        {listing.stipend && (
                          <span className="flex items-center space-x-1 text-accentGreen font-semibold">
                            <DollarSign className="w-3 h-3" />
                            <span>{listing.stipend}</span>
                          </span>
                        )}
                        {listing.deadline && (
                          <span className="flex items-center space-x-1">
                            <Clock className="w-3 h-3" />
                            <span>Due {listing.deadline}</span>
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Bookmark action */}
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() =>
                          toggleSaveMutation.mutate({
                            listingId: listing.id,
                            isSaved: !!listing.is_saved,
                          })
                        }
                        title={listing.is_saved ? "Remove from shortlist" : "Save to shortlist"}
                        className={`p-2.5 rounded-btn border transition-all ${
                          listing.is_saved
                            ? "bg-accentBlue text-white border-accentBlue shadow-2xs"
                            : "bg-surface hover:bg-canvas text-secondaryText hover:text-primaryText border-softBorder"
                        }`}
                      >
                        <Bookmark className="w-4 h-4" />
                      </button>

                      <a
                        href={listing.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="p-2.5 rounded-btn bg-surface hover:bg-canvas text-secondaryText hover:text-primaryText border border-softBorder transition-all"
                        title="View original posting"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                  </div>

                  {/* Required skills */}
                  {listing.required_skills && listing.required_skills.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      {listing.required_skills.map((skill) => (
                        <span
                          key={skill}
                          className="px-2.5 py-1 rounded-btn bg-canvas border border-softBorder text-[11px] font-medium text-secondaryText"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Match justification accordion */}
                  {listing.match && (
                    <div className="pt-2 border-t border-softBorder/60">
                      <button
                        onClick={() =>
                          setExpandedMatchId(isExpanded ? null : listing.id)
                        }
                        className="text-xs font-semibold text-accentBlue hover:text-accentBlue-hover flex items-center space-x-1 transition-colors"
                      >
                        <span>Why you match</span>
                        {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                      </button>

                      {isExpanded && (
                        <div className="mt-3 p-3.5 rounded-btn bg-canvas border border-softBorder text-xs text-secondaryText space-y-2.5">
                          <p className="leading-relaxed font-normal text-primaryText">
                            {listing.match.justification}
                          </p>

                          {listing.match.strengths && listing.match.strengths.length > 0 && (
                            <div className="flex flex-wrap items-center gap-1.5">
                              <span className="font-semibold text-accentGreen text-[10px] uppercase tracking-wider">
                                Key Strengths:
                              </span>
                              {listing.match.strengths.map((st) => (
                                <span
                                  key={st}
                                  className="px-2 py-0.5 rounded-btn bg-accentGreen-subtle text-accentGreen font-medium text-[10px]"
                                >
                                  {st}
                                </span>
                              ))}
                            </div>
                          )}

                          {listing.match.gaps && listing.match.gaps.length > 0 && (
                            <div className="flex flex-wrap items-center gap-1.5">
                              <span className="font-semibold text-secondaryText text-[10px] uppercase tracking-wider">
                                Potential Gaps:
                              </span>
                              {listing.match.gaps.map((gap) => (
                                <span
                                  key={gap}
                                  className="px-2 py-0.5 rounded-btn bg-softBorder/50 text-secondaryText font-medium text-[10px]"
                                >
                                  {gap}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
