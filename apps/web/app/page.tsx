"use client";

import Link from "next/link";
import { motion, type Variants } from "framer-motion";
import { 
  ArrowRight, 
  Sparkles, 
  Briefcase, 
  Bot, 
  Play, 
  CheckCircle2, 
  ShieldCheck, 
  Zap, 
  Globe, 
  Headphones, 
  Database, 
  TrendingUp, 
  Star, 
  Users, 
  Search, 
  Lock, 
  Layers, 
  ChevronRight, 
  Award,
  Flame
} from "lucide-react";

export default function LandingPage() {
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.12,
        delayChildren: 0.05,
      },
    },
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
    show: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, ease: "easeOut" },
    },
  };

  const stats = [
    { label: "Active Roles Scraped & Indexed", value: "50,000+", change: "Continuously updated 24/7" },
    { label: "Average Semantic Fit Accuracy", value: "94.8%", change: "Powered by pgvector HNSW" },
    { label: "Weekly Audio Digest Runtime", value: "60-90s", change: "Monday morning briefings" },
    { label: "Spam, Duplicate & Ghost Roles", value: "0", change: "Strict algorithmic hygiene" },
  ];

  const features = [
    {
      icon: <Globe className="w-6 h-6 text-accentBlue" />,
      tag: "Live Ingestion",
      title: "Autonomous Multi-Portal Scrapers",
      description:
        "Continuously crawls public repositories, Y Combinator startup boards, RemoteOK, and corporate job hubs. Intelligent deduplication and structured LLM extraction normalize messy postings into standardized engineering profiles.",
      link: "/discover",
      linkText: "Explore live feeds",
    },
    {
      icon: <Database className="w-6 h-6 text-accentGreen" />,
      tag: "Neural Retrieval",
      title: "pgvector Semantic Match Engine",
      description:
        "Bypasses brittle keyword matching. Nexus converts your resume and job requirements into high-dimensional vector embeddings, identifying deep architectural alignment and generating clear, evidence-based justifications.",
      link: "/resume",
      linkText: "Upload profile",
    },
    {
      icon: <Bot className="w-6 h-6 text-accentYellow" />,
      tag: "Autonomous Copilot",
      title: "Tool-Calling AI Career Agent",
      description:
        "Ask questions in natural language. The Nexus agent calls internal database tools to inspect deadline proximity, pinpoint skill overlap, draft personalized interview talking points, and bookmark opportunities.",
      link: "/agent",
      linkText: "Chat with agent",
    },
    {
      icon: <Headphones className="w-6 h-6 text-accentBlue" />,
      tag: "Executive Media",
      title: "Weekly Audio & Voice Digests",
      description:
        "Wake up every Monday to a studio-synthesized audio digest tailored specifically to your active resume. Listen via 44.1kHz stereo audio stream or interactive in-browser AI narration while you commute.",
      link: "/briefings",
      linkText: "Listen to sample",
    },
  ];

  const steps = [
    {
      num: "01",
      title: "Drop Your Resume Once",
      desc: "Upload your PDF. Nexus parses extracted skills, engineering projects, and architecture experience into a private vector profile.",
    },
    {
      num: "02",
      title: "Neural Matching Across 50K+ Roles",
      desc: "Every newly scraped listing is automatically evaluated against your background, calculating granular fit percentages and evidence.",
    },
    {
      num: "03",
      title: "Priority Deadline Radar",
      desc: "Shortlist opportunities and monitor urgent roles closing within 7 days with proactive reminders and instant application source links.",
    },
    {
      num: "04",
      title: "Weekly Audio & Agent Intelligence",
      desc: "Receive weekly executive audio briefings synthesizing your top 3 matches and consult your AI copilot for tailored interview prep.",
    },
  ];

  const testimonials = [
    {
      quote:
        "Nexus surfaced a high-conviction Y Combinator backend engineer role that was buried beneath spam on typical boards. The fit percentage and evidence justification were spot on.",
      author: "Alex Mercer",
      role: "Distributed Systems Engineer",
      company: "Ex-Stripe Intern",
      stars: 5,
    },
    {
      quote:
        "The weekly executive audio digest has completely replaced my hours of mindless job board doom-scrolling. I listen on Monday morning and know exactly where to apply.",
      author: "Priya Kasturirangan",
      role: "Cloud Platform Dev",
      company: "BITS Pilani Alum",
      stars: 5,
    },
    {
      quote:
        "Asking the AI agent 'Which remote roles closing this week value Go and Kubernetes?' gave me an instant targeted shortlist with direct source links. Game changer.",
      author: "David Thorne",
      role: "Senior Infrastructure Engineer",
      company: "Tech Lead",
      stars: 5,
    },
  ];

  return (
    <div className="flex flex-col bg-canvas text-primaryText min-h-[calc(100vh-4rem)] overflow-hidden">
      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 pt-16 pb-20 md:pt-24 md:pb-28 flex flex-col lg:flex-row items-center gap-16">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="flex-1 space-y-8 max-w-2xl"
        >
          {/* Headline */}
          <motion.h1
            variants={itemVariants}
            className="font-display text-5xl md:text-7xl font-bold tracking-tight text-primaryText leading-[1.08]"
          >
            Your career search, <br className="hidden md:inline" />
            <span className="text-secondaryText">without the</span> headache.
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            variants={itemVariants}
            className="text-lg md:text-xl text-secondaryText font-normal leading-relaxed"
          >
            Stop hunting through 47 fragmented tabs. Nexus continuously scrapes public opportunities,
            understands your resume with AI, semantically matches high-signal roles, and delivers a concise weekly briefing.
          </motion.p>

          {/* CTA buttons */}
          <motion.div variants={itemVariants} className="flex flex-wrap items-center gap-4 pt-2">
            <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
              <Link
                href="/signup"
                className="px-7 py-3.5 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white font-medium text-base shadow-sm transition-all flex items-center space-x-2"
              >
                <span>Get started free</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </motion.div>
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Link
                href="/discover"
                className="px-6 py-3.5 rounded-btn bg-surface hover:bg-softBorder/30 border border-softBorder text-primaryText font-medium text-base transition-colors"
              >
                Explore live roles
              </Link>
            </motion.div>
          </motion.div>

          {/* Feature Highlights */}
          <motion.div
            variants={itemVariants}
            className="pt-6 grid grid-cols-3 gap-6 border-t border-softBorder/70 text-xs text-secondaryText"
          >
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-accentBlue" />
              <span>Resume Intelligence</span>
            </div>
            <div className="flex items-center space-x-2">
              <Bot className="w-4 h-4 text-accentGreen" />
              <span>Tool-calling agent</span>
            </div>
            <div className="flex items-center space-x-2">
              <Play className="w-4 h-4 text-accentYellow" />
              <span>Generated briefings</span>
            </div>
          </motion.div>
        </motion.div>

        {/* Product Preview Card with Framer Motion */}
        <motion.div
          initial={{ opacity: 0, scale: 0.93, y: 30 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.25, ease: [0.16, 1, 0.3, 1] }}
          className="flex-1 w-full max-w-lg lg:max-w-xl"
        >
          <motion.div
            whileHover={{ y: -6, transition: { duration: 0.25 } }}
            className="bg-surface rounded-container p-6 border border-softBorder shadow-sm relative overflow-hidden transition-shadow hover:shadow-md"
          >
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
              <motion.div
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
                className="px-3 py-1 rounded-pill bg-accentGreen-subtle text-accentGreen font-bold text-xs"
              >
                94% Match
              </motion.div>
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
                {["Go", "Kubernetes", "PostgreSQL", "FastAPI", "gRPC"].map((skill, index) => (
                  <motion.span
                    key={skill}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.4 + index * 0.06 }}
                    whileHover={{ scale: 1.06, transition: { duration: 0.15 } }}
                    className="px-2.5 py-1 rounded-pill bg-canvas border border-softBorder text-[11px] font-medium text-primaryText cursor-default"
                  >
                    {skill}
                  </motion.span>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-softBorder flex items-center justify-between text-xs text-secondaryText">
              <span>Deadline: Sep 24, 2026</span>
              <Link href="/discover" className="font-medium text-accentBlue hover:underline cursor-pointer">
                View Details →
              </Link>
            </div>
          </motion.div>
        </motion.div>
      </main>

      {/* Publicity & Trust Banner */}
      <section className="border-y border-softBorder bg-surface/50 py-8">
        <div className="max-w-7xl mx-auto px-6">
          <p className="text-center text-xs font-semibold uppercase tracking-widest text-secondaryText mb-6">
            Trusted by top engineering candidates from leading universities and tech hubs
          </p>
          <div className="flex flex-wrap items-center justify-center gap-8 md:gap-14 text-secondaryText font-display font-semibold text-sm sm:text-base">
            <span className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-accentBlue"></span>
              <span>Y Combinator Portals</span>
            </span>
            <span className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-accentGreen"></span>
              <span>GitHub Tech Repositories</span>
            </span>
            <span className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-accentYellow"></span>
              <span>RemoteOK API Feeds</span>
            </span>
            <span className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-purple-500"></span>
              <span>Workday & Greenhouse</span>
            </span>
          </div>
        </div>
      </section>

      {/* Live Metrics Grid with Scroll Animation */}
      <section className="py-20 bg-canvas">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
                className="bg-surface rounded-card p-6 border border-softBorder shadow-2xs space-y-2"
              >
                <div className="font-display text-4xl font-bold text-primaryText tracking-tight">
                  {stat.value}
                </div>
                <div className="font-medium text-xs text-primaryText">
                  {stat.label}
                </div>
                <p className="text-[11px] text-secondaryText">
                  {stat.change}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Pillars Grid */}
      <section className="py-20 bg-surface/40 border-t border-softBorder">
        <div className="max-w-7xl mx-auto px-6 space-y-14">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.5 }}
            className="text-center space-y-3 max-w-2xl mx-auto"
          >
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-pill bg-surface border border-softBorder text-xs font-semibold text-accentBlue shadow-2xs">
              <Zap className="w-3.5 h-3.5" />
              <span>Full-Stack Engineering Intelligence</span>
            </div>
            <h2 className="font-display text-3xl md:text-5xl font-bold tracking-tight text-primaryText">
              Engineered to replace fragmented job boards.
            </h2>
            <p className="text-secondaryText text-sm md:text-base leading-relaxed">
              Traditional job portals rely on stale manual posts and primitive keyword filters. Nexus combines autonomous scrapers with semantic vectors and AI voice media.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 28 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.5, delay: index * 0.12 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
                className="bg-surface rounded-container p-8 border border-softBorder shadow-2xs flex flex-col justify-between space-y-6 hover:border-softBorder/80 transition-all"
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="w-12 h-12 rounded-2xl bg-canvas flex items-center justify-center shadow-2xs border border-softBorder/60">
                      {feature.icon}
                    </div>
                    <span className="px-3 py-1 rounded-pill bg-canvas border border-softBorder text-[11px] font-semibold text-secondaryText">
                      {feature.tag}
                    </span>
                  </div>

                  <h3 className="font-display text-xl font-bold text-primaryText tracking-tight">
                    {feature.title}
                  </h3>
                  <p className="text-xs md:text-sm text-secondaryText leading-relaxed">
                    {feature.description}
                  </p>
                </div>

                <div className="pt-4 border-t border-softBorder/60">
                  <Link
                    href={feature.link}
                    className="inline-flex items-center space-x-1.5 text-xs font-semibold text-accentBlue hover:text-accentBlue-hover transition-colors"
                  >
                    <span>{feature.linkText}</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works - Step Progression */}
      <section className="py-24 bg-canvas">
        <div className="max-w-7xl mx-auto px-6 space-y-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.5 }}
            className="text-center space-y-3 max-w-xl mx-auto"
          >
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-pill bg-surface border border-softBorder text-xs font-semibold text-secondaryText shadow-2xs">
              <Layers className="w-3.5 h-3.5 text-accentGreen" />
              <span>Simple 4-Step Process</span>
            </div>
            <h2 className="font-display text-3xl md:text-4xl font-bold tracking-tight text-primaryText">
              How Nexus Works
            </h2>
            <p className="text-secondaryText text-xs md:text-sm leading-relaxed">
              From PDF drop to targeted applications in minutes.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {steps.map((step, index) => (
              <motion.div
                key={step.num}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-surface rounded-card p-6 border border-softBorder shadow-2xs space-y-3 relative"
              >
                <div className="font-display text-2xl font-bold text-accentBlue/80">
                  {step.num}
                </div>
                <h3 className="font-bold text-sm text-primaryText">
                  {step.title}
                </h3>
                <p className="text-xs text-secondaryText leading-relaxed">
                  {step.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Comparison: Legacy Boards vs Nexus */}
      <section className="py-20 bg-surface/50 border-t border-softBorder">
        <div className="max-w-6xl mx-auto px-6 space-y-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-center space-y-3 max-w-xl mx-auto"
          >
            <h2 className="font-display text-3xl font-bold tracking-tight text-primaryText">
              The Modern Job Hunting Disparity
            </h2>
            <p className="text-secondaryText text-xs md:text-sm">
              See how autonomous intelligence stacks up against traditional search.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="p-8 rounded-container bg-canvas border border-accentRed/30 space-y-4"
            >
              <h3 className="font-bold text-base text-accentRed flex items-center space-x-2">
                <span>✕</span>
                <span>Traditional Job Hunting</span>
              </h3>
              <ul className="space-y-3 text-xs text-secondaryText leading-relaxed">
                <li className="flex items-start space-x-2">
                  <span className="text-accentRed font-bold">•</span>
                  <span>Opening 50+ tabs every morning to check different company careers pages.</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-accentRed font-bold">•</span>
                  <span>Failing keyword ATS filters because you wrote "PostgreSQL" instead of "SQL".</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-accentRed font-bold">•</span>
                  <span>Applying to ghost postings that closed weeks ago with no deadline visibility.</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-accentRed font-bold">•</span>
                  <span>Manually writing out spreadsheets to track saved links and statuses.</span>
                </li>
              </ul>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="p-8 rounded-container bg-accentGreen-subtle/50 border border-accentGreen/40 space-y-4"
            >
              <h3 className="font-bold text-base text-accentGreen flex items-center space-x-2">
                <span>✓</span>
                <span>The Nexus Autonomous Way</span>
              </h3>
              <ul className="space-y-3 text-xs text-primaryText leading-relaxed font-medium">
                <li className="flex items-start space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-accentGreen shrink-0 mt-0.5" />
                  <span>Continuous background scrapers aggregating tech roles 24/7.</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-accentGreen shrink-0 mt-0.5" />
                  <span>pgvector semantic embeddings measuring real engineering compatibility.</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-accentGreen shrink-0 mt-0.5" />
                  <span>Proactive alert badges for high-signal roles closing within 7 days.</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-accentGreen shrink-0 mt-0.5" />
                  <span>AI executive audio digests delivered weekly directly to your ears.</span>
                </li>
              </ul>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Candidate Testimonials & Publicity */}
      <section className="py-24 bg-canvas">
        <div className="max-w-7xl mx-auto px-6 space-y-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-center space-y-3 max-w-xl mx-auto"
          >
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-pill bg-surface border border-softBorder text-xs font-semibold text-accentYellow shadow-2xs">
              <Award className="w-3.5 h-3.5" />
              <span>Candidate Feedback & Endorsements</span>
            </div>
            <h2 className="font-display text-3xl md:text-4xl font-bold tracking-tight text-primaryText">
              Praise from High-Signal Builders
            </h2>
            <p className="text-secondaryText text-xs md:text-sm">
              How engineers and graduates use Nexus to bypass recruiting noise.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {testimonials.map((t, index) => (
              <motion.div
                key={t.author}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.5, delay: index * 0.12 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
                className="bg-surface rounded-card p-6 md:p-8 border border-softBorder shadow-2xs space-y-5 flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="flex items-center space-x-1 text-accentYellow">
                    {[...Array(t.stars)].map((_, i) => (
                      <Star key={i} className="w-3.5 h-3.5 fill-current" />
                    ))}
                  </div>
                  <p className="text-xs md:text-sm text-primaryText leading-relaxed italic">
                    "{t.quote}"
                  </p>
                </div>

                <div className="pt-4 border-t border-softBorder/60 flex items-center space-x-3">
                  <div className="w-9 h-9 rounded-full bg-accentBlue-subtle text-accentBlue font-bold text-xs flex items-center justify-center">
                    {t.author[0]}
                  </div>
                  <div>
                    <h4 className="font-bold text-xs text-primaryText">{t.author}</h4>
                    <p className="text-[11px] text-secondaryText">{t.role} · {t.company}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Security & Isolation Callout */}
      <section className="py-16 bg-surface border-t border-softBorder">
        <div className="max-w-4xl mx-auto px-6 text-center space-y-4">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-pill bg-canvas border border-softBorder text-xs font-semibold text-secondaryText">
            <ShieldCheck className="w-4 h-4 text-accentGreen" />
            <span>Strict Candidate Privacy & Isolation</span>
          </div>
          <h3 className="font-display text-2xl font-bold text-primaryText">
            Your resume and match data belong strictly to you.
          </h3>
          <p className="text-xs text-secondaryText max-w-xl mx-auto leading-relaxed">
            Nexus runs strict tenant-scoped database isolation. Uploaded resumes, vector embeddings, and match justifications are private to your authenticated account and are never shared or sold to third parties.
          </p>
        </div>
      </section>

      {/* Bottom CTA Banner */}
      <section className="py-24 bg-canvas">
        <div className="max-w-5xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="rounded-container bg-gradient-to-b from-surface to-canvas border border-softBorder p-8 md:p-14 text-center space-y-6 shadow-sm relative overflow-hidden"
          >
            <div className="space-y-2">
              <h2 className="font-display text-3xl md:text-5xl font-bold tracking-tight text-primaryText">
                Automate your career intelligence today.
              </h2>
              <p className="text-secondaryText text-sm max-w-xl mx-auto">
                Join hundreds of engineers who let Nexus continuously scan portals, calculate match scores, and deliver personalized audio digests.
              </p>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
              <Link
                href="/signup"
                className="px-8 py-3.5 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white text-sm font-semibold shadow-sm transition-all flex items-center space-x-2"
              >
                <span>Create free account</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/discover"
                className="px-7 py-3.5 rounded-btn bg-surface hover:bg-canvas border border-softBorder text-sm font-semibold text-primaryText transition-colors"
              >
                Browse opportunities
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-softBorder py-10 bg-surface text-xs text-secondaryText">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2026 Nexus Intelligence. Autonomous career intelligence and semantic retrieval.</p>
          <div className="flex items-center space-x-6">
            <Link href="/discover" className="hover:text-primaryText transition-colors">Discover</Link>
            <Link href="/shortlist" className="hover:text-primaryText transition-colors">Shortlist</Link>
            <Link href="/briefings" className="hover:text-primaryText transition-colors">Briefings</Link>
            <Link href="/agent" className="hover:text-primaryText transition-colors">AI Agent</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
