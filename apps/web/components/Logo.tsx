"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { useTheme } from "@/lib/theme-context";

interface LogoProps {
  width?: number;
  height?: number;
  priority?: boolean;
  className?: string;
  alt?: string;
}

export function Logo({
  width = 160,
  height = 42,
  priority = false,
  className = "h-8 md:h-9 w-auto object-contain transition-transform",
  alt = "Nexus Career Intelligence",
}: LogoProps) {
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Before hydration, check if dark class is present or default to dark
  // to minimize layout shifts on dark mode users.
  const isDark = mounted
    ? resolvedTheme === "dark"
    : typeof document !== "undefined" && document.documentElement.classList.contains("dark");

  const logoSrc = isDark
    ? "/logo_dark_transparent.png"
    : "/logo_light_transparent.png";

  return (
    <Image
      src={logoSrc}
      alt={alt}
      width={width}
      height={height}
      priority={priority}
      className={className}
    />
  );
}
