"use client";

import { motion } from "framer-motion";
import {
  Bookmark,
  ExternalLink,
  Sparkles,
  MapPin,
  DollarSign,
  Clock,
  ChevronDown,
  ChevronUp,
  Building2,
  Globe,
} from "lucide-react";
import type { ListingItem } from "@/types";

interface ListingCardProps {
  listing: ListingItem;
  index: number;
  isExpanded: boolean;
  onToggleExpand: (id: string) => void;
  isSaved: boolean;
  onToggleSave: (listingId: string, isSaved: boolean) => void;
  isSaving?: boolean;
}

function decodeEntities(text: string | null | undefined): string {
  if (!text) return "";
  return text
    .replace(/&amp;/g, "&")
    .replace(/&#039;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/Â·/g, "·")
    .replace(/\uFFFD/g, "–");
}

export function ListingCard({
  listing,
  index,
  isExpanded,
  onToggleExpand,
  isSaved,
  onToggleSave,
  isSaving = false,
}: ListingCardProps) {
  const calculateDaysRemaining = (deadlineStr: string | null): number | null => {
    if (!deadlineStr) return null;
    const deadline = new Date(deadlineStr);
    const today = new Date();
    const diffTime = deadline.getTime() - today.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const daysRemaining = calculateDaysRemaining(listing.deadline);
  const isClosingSoon =
    daysRemaining !== null && daysRemaining <= 7 && daysRemaining >= 0;
  const matchScore = listing.match_score;

  // Clean values for visual rendering
  const title = decodeEntities(listing.title);
  const company = decodeEntities(listing.company);
  const location = decodeEntities(listing.location);
  const stipend = decodeEntities(listing.stipend);

  const getExperienceBadgeClass = (exp?: string | null) => {
    if (!exp) return null;
    const lower = exp.toLowerCase();
    if (lower.includes("intern")) {
      return "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30";
    }
    if (lower.includes("senior") || lower.includes("staff")) {
      return "bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/30";
    }
    if (lower.includes("lead") || lower.includes("principal")) {
      return "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30";
    }
    if (lower.includes("entry") || lower.includes("junior")) {
      return "bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/30";
    }
    return "bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-indigo-500/30";
  };

  const expBadgeClass = getExperienceBadgeClass(listing.experience_level);

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: Math.min(index * 0.04, 0.4) }}
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
      className="bg-surface rounded-card p-6 border border-softBorder hover:border-softBorder/80 transition-all shadow-2xs space-y-4"
    >
      {/* Top row: match badge, title, save action */}
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-2 flex-1 min-w-0">
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
                <span>Unscored (Sign in & Upload Resume)</span>
              </div>
            )}

            {listing.remote_ok && (
              <div className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-pill text-xs font-semibold bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/25">
                <Globe className="w-3 h-3" />
                <span>Remote</span>
              </div>
            )}

            {listing.experience_level && expBadgeClass && (
              <div
                className={`inline-flex items-center px-2.5 py-0.5 rounded-pill text-xs font-semibold border ${expBadgeClass}`}
              >
                <span>{listing.experience_level}</span>
              </div>
            )}

            {isClosingSoon && (
              <div className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-pill text-xs font-bold bg-accentYellow-subtle text-amber-700 border border-amber-300">
                <Clock className="w-3 h-3" />
                <span>Closing in {daysRemaining} days</span>
              </div>
            )}
          </div>

          <h2 className="text-lg font-bold text-primaryText tracking-tight break-words">
            {title}
          </h2>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-secondaryText font-medium">
            <span className="inline-flex items-center space-x-1 font-semibold text-primaryText">
              <Building2 className="w-3.5 h-3.5 text-secondaryText/80" />
              <span>{company}</span>
            </span>
            <span className="inline-flex items-center space-x-1">
              <MapPin className="w-3.5 h-3.5 text-secondaryText/80" />
              <span>
                {location || (listing.remote_ok ? "Remote" : "Location flexible")}
              </span>
            </span>
            {stipend && (
              <span className="inline-flex items-center space-x-1 text-accentGreen font-semibold">
                <DollarSign className="w-3.5 h-3.5" />
                <span>{stipend}</span>
              </span>
            )}
            {listing.deadline && (
              <span className="inline-flex items-center space-x-1">
                <Clock className="w-3.5 h-3.5 text-secondaryText/80" />
                <span>Due {listing.deadline}</span>
              </span>
            )}
          </div>
        </div>

        {/* Bookmark and external link actions */}
        <div className="flex items-center space-x-2 shrink-0">
          <button
            onClick={() => onToggleSave(listing.id, isSaved)}
            disabled={isSaving}
            title={isSaved ? "Remove from shortlist" : "Save to shortlist"}
            className={`p-2.5 rounded-btn border transition-all ${
              isSaved
                ? "bg-accentBlue text-white border-accentBlue shadow-2xs"
                : "bg-surface hover:bg-canvas text-secondaryText hover:text-primaryText border-softBorder"
            } disabled:opacity-50`}
          >
            <Bookmark className="w-4 h-4" />
          </button>

          {listing.source_url && (
            <a
              href={listing.source_url}
              target="_blank"
              rel="noreferrer"
              className="p-2.5 rounded-btn bg-surface hover:bg-canvas text-secondaryText hover:text-primaryText border border-softBorder transition-all"
              title="View original posting"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
        </div>
      </div>

      {/* Required skills */}
      {listing.required_skills && listing.required_skills.length > 0 && (
        <div className="flex flex-wrap items-center gap-1.5 pt-1">
          {listing.required_skills.map((skill) => (
            <span
              key={skill}
              className="px-2.5 py-1 rounded-md bg-canvas border border-softBorder/80 text-[11px] font-medium text-secondaryText hover:text-primaryText hover:border-accentBlue/30 transition-colors"
            >
              {decodeEntities(skill)}
            </span>
          ))}
        </div>
      )}

      {/* Match justification accordion */}
      {listing.match_explanation && (
        <div className="pt-2 border-t border-softBorder/60">
          <button
            onClick={() => onToggleExpand(listing.id)}
            className="text-xs font-semibold text-accentBlue hover:text-accentBlue-hover flex items-center space-x-1 transition-colors"
          >
            <span>Why you match</span>
            {isExpanded ? (
              <ChevronUp className="w-3.5 h-3.5" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5" />
            )}
          </button>

          {isExpanded && (
            <div className="mt-3 p-3.5 rounded-btn bg-canvas border border-softBorder text-xs text-primaryText leading-relaxed">
              {listing.match_explanation}
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
}
