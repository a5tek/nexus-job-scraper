import Link from "next/link";
import { ArrowRight, Sparkles, Briefcase, FileText, Bot, Play } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-canvas text-primaryText">
      {/* Workspace / Context Navigation Header */}
      <header className="w-full max-w-7xl mx-auto px-6 py-6 flex items-center justify-between border-b border-softBorder/60">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-primaryText text-surface flex items-center justify-center font-bold text-sm tracking-widest shadow-sm">
            NX
          </div>
          <span className="font-display font-bold text-xl tracking-tight text-primaryText">NEXUS</span>
        </div>

        <nav className="hidden md:flex items-center space-x-8 text-sm font-medium text-secondaryText">
          <Link href="#how-it-works" className="hover:text-primaryText transition-colors">How it works</Link>
          <Link href="#discover" className="hover:text-primaryText transition-colors">Discover</Link>
          <Link href="#agent" className="hover:text-primaryText transition-colors">Agent</Link>
          <Link href="#briefings" className="hover:text-primaryText transition-colors">Briefings</Link>
        </nav>

        <div className="flex items-center space-x-3">
          <Link
            href="/login"
            className="px-4 py-2 rounded-btn text-sm font-medium hover:bg-softBorder/50 transition-colors"
          >
            Sign in
          </Link>
          <Link
            href="/discover"
            className="px-5 py-2.5 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white text-sm font-medium shadow-sm transition-all flex items-center space-x-2"
          >
            <span>Enter App</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 max-w-7xl mx-auto px-6 py-16 md:py-24 flex flex-col lg:flex-row items-center gap-16">
        <div className="flex-1 space-y-8 max-w-2xl">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-pill bg-white border border-softBorder text-xs font-semibold text-secondaryText shadow-xs">
            <span className="w-2 h-2 rounded-full bg-accentGreen animate-pulse"></span>
            <span>Autonomous Career Intelligence Platform</span>
          </div>

          <h1 className="font-display text-5xl md:text-7xl font-bold tracking-tight text-primaryText leading-[1.08]">
            Your career search, <br className="hidden md:inline" />
            <span className="text-secondaryText">without the</span> headache.
          </h1>

          <p className="text-lg md:text-xl text-secondaryText font-normal leading-relaxed">
            Stop hunting through 47 fragmented tabs. Nexus continuously scrapes public opportunities,
            understands your resume with AI, semantically matches high-signal roles, and delivers a concise weekly briefing.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2">
            <Link
              href="/signup"
              className="px-7 py-3.5 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white font-medium text-base shadow-sm transition-all flex items-center space-x-2"
            >
              <span>Get started free</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/discover"
              className="px-6 py-3.5 rounded-btn bg-surface hover:bg-softBorder/30 border border-softBorder text-primaryText font-medium text-base transition-colors"
            >
              Explore live roles
            </Link>
          </div>

          <div className="pt-6 grid grid-cols-3 gap-6 border-t border-softBorder/70 text-xs text-secondaryText">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-accentBlue" />
              <span>pgvector semantic match</span>
            </div>
            <div className="flex items-center space-x-2">
              <Bot className="w-4 h-4 text-accentGreen" />
              <span>Tool-calling agent</span>
            </div>
            <div className="flex items-center space-x-2">
              <Play className="w-4 h-4 text-accentYellow" />
              <span>Generated briefings</span>
            </div>
          </div>
        </div>

        {/* Product Preview Card */}
        <div className="flex-1 w-full max-w-lg lg:max-w-xl">
          <div className="bg-surface rounded-container p-6 border border-softBorder shadow-sm relative overflow-hidden">
            <div className="flex items-center justify-between pb-5 border-b border-softBorder">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-canvas flex items-center justify-center text-primaryText">
                  <Briefcase className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-semibold text-sm text-primaryText">Distributed Systems Intern</h3>
                  <p className="text-xs text-secondaryText">CloudScale Labs · Remote · ₹45,000/mo</p>
                </div>
              </div>
              <div className="px-3 py-1 rounded-pill bg-accentGreen-subtle text-accentGreen font-bold text-xs">
                94% Match
              </div>
            </div>

            <div className="py-4 space-y-3">
              <div className="p-3.5 rounded-btn bg-canvas/70 border border-softBorder/60 text-xs">
                <div className="flex items-center space-x-1.5 font-semibold text-accentBlue mb-1">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Why Nexus thinks you fit</span>
                </div>
                <p className="text-secondaryText leading-relaxed">
                  Strong match because your backend projects and PostgreSQL experience align directly with this role’s distributed storage and API infrastructure requirements.
                </p>
              </div>

              <div className="flex flex-wrap gap-2 pt-1">
                {["Go", "Kubernetes", "PostgreSQL", "FastAPI", "gRPC"].map((skill) => (
                  <span
                    key={skill}
                    className="px-2.5 py-1 rounded-pill bg-white border border-softBorder text-[11px] font-medium text-primaryText"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-softBorder flex items-center justify-between text-xs text-secondaryText">
              <span>Deadline: Sep 24, 2026</span>
              <span className="font-medium text-accentBlue hover:underline cursor-pointer">View Details →</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
