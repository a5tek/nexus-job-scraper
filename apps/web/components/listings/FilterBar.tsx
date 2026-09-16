"use client";

import {
  Search,
  SlidersHorizontal,
  Globe,
  CheckCircle2,
  Sparkles,
  Loader2,
  X,
} from "lucide-react";

interface FilterBarProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  onSearchSubmit: (e: React.FormEvent) => void;
  onClearSearch?: () => void;
  isSearching?: boolean;
  remoteOnly: boolean;
  onToggleRemote: () => void;
  minFit: number | null;
  onSelectMinFit: (fit: number | null) => void;
  totalShown: number;
  isLoading: boolean;
}

export function FilterBar({
  searchQuery,
  onSearchChange,
  onSearchSubmit,
  onClearSearch,
  isSearching = false,
  remoteOnly,
  onToggleRemote,
  minFit,
  onSelectMinFit,
  totalShown,
  isLoading,
}: FilterBarProps) {
  return (
    <div className="bg-surface rounded-card p-4 border border-softBorder shadow-xs space-y-4">
      <form onSubmit={onSearchSubmit} className="flex gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-secondaryText absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search roles, skills, or tech stack (e.g., 'distributed systems Golang', 'AI agents Python')..."
            className="w-full pl-10 pr-10 py-2.5 rounded-btn bg-canvas border border-softBorder text-sm text-primaryText placeholder:text-secondaryText/60 focus:outline-none focus:ring-2 focus:ring-accentBlue/20 focus:border-accentBlue transition-all"
          />
          {searchQuery && onClearSearch && (
            <button
              type="button"
              onClick={onClearSearch}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-secondaryText hover:text-primaryText p-1"
              title="Clear search"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
        <button
          type="submit"
          disabled={isSearching}
          className="px-5 py-2.5 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white text-sm font-semibold shadow-xs transition-all flex items-center space-x-2 shrink-0 disabled:opacity-70"
        >
          {isSearching ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Searching...</span>
            </>
          ) : (
            <span>Search</span>
          )}
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
            onClick={onToggleRemote}
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
            onClick={() => onSelectMinFit(minFit === 75 ? null : 75)}
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
            onClick={() => onSelectMinFit(minFit === 90 ? null : 90)}
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
          {isLoading ? "Loading..." : `${totalShown} opportunities shown`}
        </div>
      </div>
    </div>
  );
}
