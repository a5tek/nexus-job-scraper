"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Compass,
  Bookmark,
  FileText,
  Bot,
  Headphones,
  LogOut,
  Sparkles,
  Menu,
  X,
  LogIn,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Logo } from "@/components/Logo";

export function Navbar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  // Close mobile menu on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setMobileMenuOpen(false);
      }
    };
    if (mobileMenuOpen) {
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [mobileMenuOpen]);

  const navItems = [
    { label: "Discover", href: "/discover", icon: Compass },
    { label: "Shortlist", href: "/shortlist", icon: Bookmark },
    { label: "Resume", href: "/resume", icon: FileText },
    { label: "Agent", href: "/agent", icon: Bot },
    { label: "Briefings", href: "/briefings", icon: Headphones },
  ];

  return (
    <header className="sticky top-0 z-40 w-full bg-surface/85 backdrop-blur-md border-b border-softBorder transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand / Logo (Top Left) */}
        <div className="flex items-center space-x-8">
          <Link
            href="/"
            className="flex items-center group py-1"
            aria-label="Nexus Career Intelligence"
          >
            <motion.div
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              transition={{ type: "spring", stiffness: 400, damping: 22 }}
              className="flex items-center"
            >
              <Logo priority width={160} height={42} />
            </motion.div>
          </Link>

          {/* Desktop Nav links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive =
                pathname === item.href || pathname?.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`relative px-3 py-1.5 rounded-btn text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    isActive
                      ? "text-white"
                      : "text-secondaryText hover:text-primaryText hover:bg-canvas"
                  }`}
                >
                  {isActive && (
                    <motion.span
                      layoutId="navbar-active-indicator"
                      className="absolute inset-0 bg-accentBlue rounded-btn shadow-xs -z-10"
                      transition={{ type: "spring", stiffness: 380, damping: 30 }}
                    />
                  )}
                  <Icon className="w-3.5 h-3.5 relative z-10" />
                  <span className="relative z-10">{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Desktop User state / Theme toggle / Auth actions */}
        <div className="hidden md:flex items-center space-x-3">
          <ThemeToggle />

          {user ? (
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 px-3 py-1.5 rounded-pill bg-canvas border border-softBorder text-xs">
                <div className="w-5 h-5 rounded-full bg-accentGreen/20 text-accentGreen flex items-center justify-center font-bold text-[10px]">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                <span className="font-medium text-primaryText truncate max-w-[120px]">
                  {user.name}
                </span>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={logout}
                title="Sign out"
                className="p-2 rounded-btn text-secondaryText hover:text-accentRed hover:bg-accentRed-subtle transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </motion.button>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <Link
                href="/login"
                className="px-3.5 py-1.5 rounded-btn text-xs font-semibold text-secondaryText hover:text-primaryText hover:bg-canvas transition-colors"
              >
                Sign in
              </Link>
              <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
                <Link
                  href="/signup"
                  className="px-4 py-1.5 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white text-xs font-semibold shadow-xs transition-all flex items-center space-x-1"
                >
                  <Sparkles className="w-3 h-3" />
                  <span>Sign up</span>
                </Link>
              </motion.div>
            </div>
          )}
        </div>

        {/* Mobile menu trigger & Theme toggle */}
        <div className="flex md:hidden items-center space-x-2">
          <ThemeToggle />

          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-expanded={mobileMenuOpen}
            aria-label="Toggle navigation menu"
            className="p-2 rounded-btn bg-canvas border border-softBorder text-secondaryText hover:text-primaryText transition-colors"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={() => setMobileMenuOpen(false)}
              className="fixed inset-0 top-16 bg-black/40 backdrop-blur-xs z-40 md:hidden"
            />

            {/* Slide-out Menu Panel */}
            <motion.div
              initial={{ opacity: 0, y: -8, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -8, scale: 0.98 }}
              transition={{ duration: 0.25, ease: "easeOut" }}
              className="absolute top-16 left-0 right-0 bg-surface border-b border-softBorder shadow-lg z-50 p-4 md:hidden space-y-4 max-h-[calc(100vh-4rem)] overflow-y-auto"
            >
              {/* User Profile / Status in Mobile */}
              {user && (
                <div className="flex items-center justify-between p-3 rounded-card bg-canvas border border-softBorder">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-full bg-accentGreen/20 text-accentGreen flex items-center justify-center font-bold text-xs">
                      {user.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="space-y-0.5">
                      <p className="text-xs font-semibold text-primaryText leading-none">
                        {user.name}
                      </p>
                      <p className="text-[11px] text-secondaryText leading-none">
                        {user.email}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      logout();
                      setMobileMenuOpen(false);
                    }}
                    className="p-2 rounded-btn text-secondaryText hover:text-accentRed hover:bg-accentRed-subtle transition-colors"
                    title="Sign out"
                  >
                    <LogOut className="w-4 h-4" />
                  </button>
                </div>
              )}

              {/* Mobile Nav Links */}
              <nav className="space-y-1">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isActive =
                    pathname === item.href || pathname?.startsWith(`${item.href}/`);
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className={`flex items-center space-x-3 px-3.5 py-2.5 rounded-btn text-sm font-medium transition-colors ${
                        isActive
                          ? "bg-accentBlue text-white font-semibold shadow-2xs"
                          : "text-secondaryText hover:text-primaryText hover:bg-canvas"
                      }`}
                    >
                      <Icon className="w-4 h-4 shrink-0" />
                      <span>{item.label}</span>
                    </Link>
                  );
                })}
              </nav>

              {/* Auth links for logged out users */}
              {!user && (
                <div className="pt-3 border-t border-softBorder flex flex-col gap-2">
                  <Link
                    href="/login"
                    onClick={() => setMobileMenuOpen(false)}
                    className="w-full text-center py-2.5 rounded-btn bg-canvas border border-softBorder text-xs font-semibold text-primaryText hover:bg-softBorder/30 transition-colors flex items-center justify-center space-x-1.5"
                  >
                    <LogIn className="w-3.5 h-3.5" />
                    <span>Sign In</span>
                  </Link>
                  <Link
                    href="/signup"
                    onClick={() => setMobileMenuOpen(false)}
                    className="w-full text-center py-2.5 rounded-btn bg-accentBlue text-white text-xs font-semibold shadow-2xs hover:bg-accentBlue-hover transition-colors flex items-center justify-center space-x-1.5"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Create Account</span>
                  </Link>
                </div>
              )}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </header>
  );
}
