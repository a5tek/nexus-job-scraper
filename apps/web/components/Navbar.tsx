"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { 
  Compass, 
  Bookmark, 
  FileText, 
  Bot, 
  Headphones, 
  LogOut, 
  Sparkles
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { ThemeToggle } from "@/components/ThemeToggle";

export function Navbar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

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
          <Link href="/" className="flex items-center group py-1" aria-label="Nexus Career Intelligence">
            <motion.div
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.97 }}
              transition={{ type: "spring", stiffness: 400, damping: 22 }}
              className="flex items-center relative"
            >
              {/* Light mode logo */}
              <Image
                src="/logo_light_transparent.png"
                alt="Nexus Career Intelligence"
                width={160}
                height={42}
                priority
                className="h-8 md:h-9 w-auto object-contain dark:hidden transition-transform"
              />
              {/* Dark mode logo */}
              <Image
                src="/logo_dark_transparent.png"
                alt="Nexus Career Intelligence"
                width={160}
                height={42}
                priority
                className="h-8 md:h-9 w-auto object-contain hidden dark:block transition-transform"
              />
            </motion.div>
          </Link>

          {/* Nav links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
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

        {/* User state / Theme toggle / Auth actions */}
        <div className="flex items-center space-x-3">
          <ThemeToggle />

          {user ? (
            <div className="flex items-center space-x-3">
              <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-pill bg-canvas border border-softBorder text-xs">
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
      </div>
    </header>
  );
}
