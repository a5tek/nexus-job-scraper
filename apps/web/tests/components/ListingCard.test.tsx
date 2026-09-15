import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ListingCard } from "@/components/listings/ListingCard";
import type { ListingItem } from "@/types";

describe("ListingCard component", () => {
  const sampleListing: ListingItem = {
    id: "test-listing-1",
    title: "Senior Distributed Systems Engineer",
    company: "Nexus Labs",
    location: "San Francisco, CA",
    remote_ok: true,
    stipend: "$180,000 - $220,000",
    required_skills: ["Go", "Kubernetes", "PostgreSQL", "Kafka"],
    deadline: "2026-10-31",
    source_url: "https://example.com/job",
    match_score: 94,
    match_explanation: "Strong alignment with Go microservices and Kubernetes cluster architecture.",
    is_saved: false,
  };

  const defaultProps = {
    listing: sampleListing,
    index: 0,
    isExpanded: false,
    onToggleExpand: vi.fn(),
    isSaved: false,
    onToggleSave: vi.fn(),
    isSaving: false,
  };

  it("renders role title, company, location, and match score", () => {
    render(<ListingCard {...defaultProps} />);

    expect(screen.getByText("Senior Distributed Systems Engineer")).toBeInTheDocument();
    expect(screen.getByText("Nexus Labs")).toBeInTheDocument();
    expect(screen.getByText("San Francisco, CA")).toBeInTheDocument();
    expect(screen.getByText("94% Fit")).toBeInTheDocument();
    expect(screen.getByText("Go")).toBeInTheDocument();
    expect(screen.getByText("Kubernetes")).toBeInTheDocument();
  });

  it("calls onToggleSave when bookmark button is clicked", () => {
    render(<ListingCard {...defaultProps} />);
    const bookmarkBtn = screen.getByTitle("Save to shortlist");

    fireEvent.click(bookmarkBtn);
    expect(defaultProps.onToggleSave).toHaveBeenCalledWith("test-listing-1", false);
  });

  it("calls onToggleExpand when 'Why you match' is clicked", () => {
    render(<ListingCard {...defaultProps} />);
    const accordionBtn = screen.getByRole("button", { name: /why you match/i });

    fireEvent.click(accordionBtn);
    expect(defaultProps.onToggleExpand).toHaveBeenCalledWith("test-listing-1");
  });

  it("renders match explanation text when isExpanded is true", () => {
    render(<ListingCard {...defaultProps} isExpanded={true} />);
    expect(
      screen.getByText("Strong alignment with Go microservices and Kubernetes cluster architecture.")
    ).toBeInTheDocument();
  });
});
