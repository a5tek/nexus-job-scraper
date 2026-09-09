"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, Lock, Mail, User, AlertCircle, Loader2, Sparkles } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export default function SignupPage() {
  const router = useRouter();
  const { register } = useAuth();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await register({ name, email, password });
      router.push("/resume");
    } catch (err: any) {
      setError(err.message || "Failed to create account. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-6 bg-canvas">
      <div className="w-full max-w-md bg-surface rounded-card p-8 border border-softBorder shadow-sm space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center space-x-1 px-3 py-1 rounded-pill bg-accentBlue-subtle text-accentBlue text-xs font-semibold">
            <Sparkles className="w-3 h-3" />
            <span>Candidate Workspace</span>
          </div>
          <h1 className="font-display text-2xl font-bold text-primaryText tracking-tight">
            Create your Nexus Account
          </h1>
          <p className="text-xs text-secondaryText">
            Join Nexus to start matching your resume semantically with high-signal roles.
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-3.5 rounded-btn bg-accentRed-subtle border border-accentRed/30 text-accentRed text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-primaryText flex items-center space-x-1.5">
              <User className="w-3.5 h-3.5 text-secondaryText" />
              <span>Full Name</span>
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Alex Candidate"
              className="w-full px-3.5 py-2.5 rounded-btn bg-canvas border border-softBorder text-sm text-primaryText placeholder:text-secondaryText/60 focus:outline-none focus:ring-2 focus:ring-accentBlue/20 focus:border-accentBlue transition-all"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-primaryText flex items-center space-x-1.5">
              <Mail className="w-3.5 h-3.5 text-secondaryText" />
              <span>Email Address</span>
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="alex@example.com"
              className="w-full px-3.5 py-2.5 rounded-btn bg-canvas border border-softBorder text-sm text-primaryText placeholder:text-secondaryText/60 focus:outline-none focus:ring-2 focus:ring-accentBlue/20 focus:border-accentBlue transition-all"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-primaryText flex items-center space-x-1.5">
              <Lock className="w-3.5 h-3.5 text-secondaryText" />
              <span>Password (min. 8 characters)</span>
            </label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full px-3.5 py-2.5 rounded-btn bg-canvas border border-softBorder text-sm text-primaryText placeholder:text-secondaryText/60 focus:outline-none focus:ring-2 focus:ring-accentBlue/20 focus:border-accentBlue transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white text-sm font-semibold shadow-xs transition-all flex items-center justify-center space-x-2 disabled:opacity-60"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Creating account...</span>
              </>
            ) : (
              <>
                <span>Get started</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="pt-4 border-t border-softBorder/60 text-center text-xs text-secondaryText">
          Already have an account?{" "}
          <Link href="/login" className="text-accentBlue font-semibold hover:underline">
            Sign in here
          </Link>
        </div>
      </div>
    </div>
  );
}
