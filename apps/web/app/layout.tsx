import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Nexus — Autonomous Career Intelligence",
  description: "Find roles, understand fit, and receive personalized weekly audio/video career briefings.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-canvas text-primaryText min-h-screen antialiased selection:bg-accentBlue selection:text-white flex flex-col">
        <Providers>
          <Navbar />
          <main className="flex-1">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
