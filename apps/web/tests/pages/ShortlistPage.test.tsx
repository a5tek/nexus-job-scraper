import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ShortlistPage from "@/app/shortlist/page";
import * as apiModule from "@/lib/api";

vi.mock("@/lib/api", () => ({
  apiClient: vi.fn(),
}));

describe("ShortlistPage", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it("renders loading state cleanly without throwing TypeError when data is undefined", () => {
    vi.mocked(apiModule.apiClient).mockImplementation(() => new Promise(() => {}));

    render(<ShortlistPage />, { wrapper });

    expect(
      screen.getByText("Loading your shortlisted opportunities...")
    ).toBeInTheDocument();
  });

  it("handles array responses directly from backend and displays roles", async () => {
    vi.mocked(apiModule.apiClient).mockResolvedValue([
      {
        id: "saved-1",
        listing: {
          id: "listing-1",
          title: "Senior Backend Engineer",
          company: "Nexus Labs",
          location: "Remote",
          remote_ok: true,
          stipend: "$150,000",
          required_skills: ["Python", "FastAPI"],
          deadline: null,
          match_score: 95,
          match_explanation: "Strong match for Python backend",
          source_url: "https://example.com/job/1",
        },
      },
    ]);

    render(<ShortlistPage />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText("Senior Backend Engineer")).toBeInTheDocument();
    });
    expect(screen.getByText("Nexus Labs")).toBeInTheDocument();
    expect(screen.getByText("95% Fit")).toBeInTheDocument();
    expect(screen.getByText("Strong match for Python backend")).toBeInTheDocument();
  });

  it("handles object responses { items: [...] } correctly", async () => {
    vi.mocked(apiModule.apiClient).mockResolvedValue({
      count: 1,
      items: [
        {
          id: "saved-2",
          listing: {
            id: "listing-2",
            title: "Frontend Architect",
            company: "Tech Corp",
            location: "New York",
            remote_ok: false,
            stipend: null,
            required_skills: ["React", "TypeScript"],
            deadline: null,
            match_score: 88,
            match_explanation: "Excellent UI systems architecture fit",
            source_url: "https://example.com/job/2",
          },
        },
      ],
    });

    render(<ShortlistPage />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText("Frontend Architect")).toBeInTheDocument();
    });
    expect(screen.getByText("Tech Corp")).toBeInTheDocument();
  });

  it("renders empty state when shortlist has no items", async () => {
    vi.mocked(apiModule.apiClient).mockResolvedValue([]);

    render(<ShortlistPage />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText("Your shortlist is empty")).toBeInTheDocument();
    });
    expect(screen.getByText("Explore Discover Feed")).toBeInTheDocument();
  });
});
