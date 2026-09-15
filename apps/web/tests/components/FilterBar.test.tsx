import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { FilterBar } from "@/components/listings/FilterBar";

describe("FilterBar component", () => {
  const defaultProps = {
    searchQuery: "",
    onSearchChange: vi.fn(),
    onSearchSubmit: vi.fn(),
    onClearSearch: vi.fn(),
    isSearching: false,
    remoteOnly: false,
    onToggleRemote: vi.fn(),
    minFit: null,
    onSelectMinFit: vi.fn(),
    totalShown: 42,
    isLoading: false,
  };

  it("renders search input, filter buttons, and count", () => {
    render(<FilterBar {...defaultProps} />);

    expect(screen.getByPlaceholderText(/search semantic concepts/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^search$/i })).toBeInTheDocument();
    expect(screen.getByText(/remote only/i)).toBeInTheDocument();
    expect(screen.getByText(/high fit \(75%\+\)/i)).toBeInTheDocument();
    expect(screen.getByText(/elite fit \(90%\+\)/i)).toBeInTheDocument();
    expect(screen.getByText(/42 opportunities shown/i)).toBeInTheDocument();
  });

  it("calls onSearchChange when user types in input", () => {
    render(<FilterBar {...defaultProps} />);
    const input = screen.getByPlaceholderText(/search semantic concepts/i);

    fireEvent.change(input, { target: { value: "golang distributed" } });
    expect(defaultProps.onSearchChange).toHaveBeenCalledWith("golang distributed");
  });

  it("calls onToggleRemote when Remote Only filter is clicked", () => {
    render(<FilterBar {...defaultProps} />);
    const remoteBtn = screen.getByText(/remote only/i);

    fireEvent.click(remoteBtn);
    expect(defaultProps.onToggleRemote).toHaveBeenCalled();
  });

  it("shows loading state when isLoading is true", () => {
    render(<FilterBar {...defaultProps} isLoading={true} />);
    expect(screen.getByText(/loading\.\.\./i)).toBeInTheDocument();
  });
});
