"use client";

import Link from "next/link";
import { motion, type Variants } from "framer-motion";
import { ArrowRight, Sparkles, Briefcase, Bot, Play } from "lucide-react";

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

  return (
    <div className="flex flex-col bg-canvas text-primaryText min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <main className="flex-1 max-w-7xl mx-auto px-6 py-16 md:py-24 flex flex-col lg:flex-row items-center gap-16">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="flex-1 space-y-8 max-w-2xl"
        >
          {/* Badge */}
          <motion.div variants={itemVariants}>
            <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-pill bg-surface border border-softBorder text-xs font-semibold text-secondaryText shadow-xs">
              <span className="w-2 h-2 rounded-full bg-accentGreen animate-pulse"></span>
              <span>Autonomous Career Intelligence Platform</span>
            </div>
          </motion.div>

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
    </div>
  );
}
