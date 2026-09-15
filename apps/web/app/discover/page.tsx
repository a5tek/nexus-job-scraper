"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Sparkles, Search, AlertCircle } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ListingCard } from "@/components/listings/ListingCard";
import { FilterBar } from "@/components/listings/FilterBar";
import type { ListingItem } from "@/types";

export default function DiscoverPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [searchQuery, setSearchQuery] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [minFit, setMinFit] = useState<number | null>(null);
  const [expandedMatchId, setExpandedMatchId] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  // Fetch opportunity listings
  const { data, isLoading, error } = useQuery<ListingItem[]>({
    queryKey: ["listings", remoteOnly],
    queryFn: async () => {
      let endpoint = `/listings?limit=30`;
      if (remoteOnly) endpoint += `&remote_only=true`;
      const res = await apiClient<ListingItem[] | { items: ListingItem[] }>(endpoint);
      return Array.isArray(res) ? res : res?.items || [];
    },
  });

  // Toggle Shortlist mutation
  const toggleSaveMutation = useMutation({
    mutationFn: async ({
      listingId,
      isSaved,
    }: {
      listingId: string;
      isSaved: boolean;
    }) => {
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
    setSearchError(null);

    if (!searchQuery.trim()) {
      queryClient.invalidateQueries({ queryKey: ["listings"] });
      return;
    }

    setIsSearching(true);
    try {
      const searchRes = await apiClient<ListingItem[] | { items: ListingItem[] }>(
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
      const items = Array.isArray(searchRes) ? searchRes : searchRes?.items || [];
      queryClient.setQueryData(["listings", remoteOnly], items);
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : "Search failed. Please check your network and try again.";
      setSearchError(message);
    } finally {
      setIsSearching(false);
    }
  };

  const handleClearSearch = () => {
    setSearchQuery("");
    setSearchError(null);
    queryClient.invalidateQueries({ queryKey: ["listings"] });
  };

  const allItems = Array.isArray(data) ? data : [];
  const items = minFit
    ? allItems.filter((i) => (i.match_score ?? 0) >= minFit)
    : allItems;

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-canvas py-8 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-pill bg-surface border border-softBorder text-xs font-semibold text-secondaryText mb-2 shadow-2xs">
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

        {/* Search & Filter Bar Subcomponent */}
        <FilterBar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onSearchSubmit={handleSearch}
          onClearSearch={handleClearSearch}
          isSearching={isSearching}
          remoteOnly={remoteOnly}
          onToggleRemote={() => setRemoteOnly(!remoteOnly)}
          minFit={minFit}
          onSelectMinFit={setMinFit}
          totalShown={items.length}
          isLoading={isLoading}
        />

        {/* Search Error Alert */}
        {searchError && (
          <div className="p-4 rounded-card bg-accentRed-subtle border border-accentRed/30 text-accentRed text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span className="flex-1">{searchError}</span>
            <button
              onClick={() => setSearchError(null)}
              className="text-accentRed underline font-semibold ml-2"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Listings Feed */}
        {isLoading ? (
          <div className="py-16 text-center space-y-3">
            <div className="w-8 h-8 mx-auto rounded-full border-2 border-accentBlue border-t-transparent animate-spin"></div>
            <p className="text-xs text-secondaryText font-medium">Loading opportunities...</p>
          </div>
        ) : error ? (
          <div className="p-6 bg-surface rounded-card border border-accentRed/30 text-center space-y-2">
            <p className="text-sm font-semibold text-accentRed">Unable to load opportunities</p>
            <p className="text-xs text-secondaryText">Ensure the backend API is running at localhost:8000.</p>
          </div>
        ) : items.length === 0 ? (
          <div className="py-16 text-center bg-surface rounded-card border border-softBorder p-8 space-y-3">
            <div className="w-12 h-12 mx-auto rounded-2xl bg-canvas flex items-center justify-center text-secondaryText">
              <Search className="w-6 h-6" />
            </div>
            <h3 className="font-semibold text-base text-primaryText">No matching roles found</h3>
            <p className="text-xs text-secondaryText max-w-md mx-auto">
              Try broadening your search query or removing filters.
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {items.map((listing, index) => (
              <ListingCard
                key={listing.id}
                listing={listing}
                index={index}
                isExpanded={expandedMatchId === listing.id}
                onToggleExpand={(id) =>
                  setExpandedMatchId(expandedMatchId === id ? null : id)
                }
                isSaved={!!listing.is_saved}
                onToggleSave={(listingId, isSaved) =>
                  toggleSaveMutation.mutate({ listingId, isSaved })
                }
                isSaving={toggleSaveMutation.isPending}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
