"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  Compass, 
  Bookmark, 
  FileText, 
  Bot, 
  Headphones, 
  LogOut, 
  User as UserIcon,
  Sparkles
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";

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
    <header className="sticky top-0 z-40 w-full bg-surface/85 backdrop-blur-md border-b border-softBorder">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-8">
          <Link href="/" className="flex items-center space-x-2.5 group">
            <div className="w-8 h-8 rounded-xl bg-primaryText text-white flex items-center justify-center font-bold text-xs tracking-wider shadow-sm transition-transform group-hover:scale-105">
              NX
            </div>
            <div className="flex flex-col">
              <span className="font-display font-bold text-base tracking-tight text-primaryText leading-none">
                NEXUS
              </span>
              <span className="text-[10px] text-secondaryText font-medium tracking-wide">
                CAREER INTELLIGENCE
              </span>
            </div>
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
                  className={`px-3 py-1.5 rounded-btn text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    isActive
                      ? "bg-accentBlue text-white shadow-xs"
                      : "text-secondaryText hover:text-primaryText hover:bg-canvas"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* User state / Auth actions */}
        <div className="flex items-center space-x-3">
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
              <button
                onClick={logout}
                title="Sign out"
                className="p-2 rounded-btn text-secondaryText hover:text-accentRed hover:bg-accentRed-subtle transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <Link
                href="/login"
                className="px-3.5 py-1.5 rounded-btn text-xs font-semibold text-secondaryText hover:text-primaryText hover:bg-canvas transition-colors"
              >
                Sign in
              </Link>
              <Link
                href="/signup"
                className="px-4 py-1.5 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white text-xs font-semibold shadow-xs transition-all flex items-center space-x-1"
              >
                <Sparkles className="w-3 h-3" />
                <span>Sign up</span>
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
