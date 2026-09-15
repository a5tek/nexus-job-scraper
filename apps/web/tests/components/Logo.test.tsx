import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { Logo } from "@/components/Logo";

// Mock useTheme
vi.mock("@/lib/theme-context", () => ({
  useTheme: () => ({
    resolvedTheme: "dark",
    theme: "dark",
    setTheme: vi.fn(),
    toggleTheme: vi.fn(),
  }),
}));

describe("Logo component", () => {
  it("renders the logo with alt text", () => {
    render(<Logo alt="Nexus Test Logo" />);
    const img = screen.getByAltText("Nexus Test Logo");
    expect(img).toBeInTheDocument();
    expect(img.getAttribute("src")).toContain("logo_dark_transparent.png");
  });

  it("applies custom width and height attributes", () => {
    render(<Logo width={200} height={50} />);
    const img = screen.getByAltText("Nexus Career Intelligence");
    expect(img).toHaveAttribute("width", "200");
    expect(img).toHaveAttribute("height", "50");
  });
});
