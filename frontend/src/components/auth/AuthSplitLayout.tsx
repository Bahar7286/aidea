"use client";

import Link from "next/link";
import { ReactNode } from "react";
import { Leaf } from "lucide-react";
import { AuthFieldVisual } from "@/components/auth/AuthFieldVisual";

type AuthSplitLayoutProps = {
  children: ReactNode;
  panelTitle: string;
  panelSubtitle: string;
  panelTone?: "login" | "register" | "verify" | "role" | "forgot";
  /** Wider form column for role / multi-field screens */
  wide?: boolean;
};

const panelArt: Record<string, string> = {
  login: "bg-gradient-to-br from-[#081c15] via-[#1b4332] to-[#2d6a4f]",
  register: "bg-gradient-to-br from-[#081c15] via-[#1b4332] to-[#40916c]",
  verify: "bg-gradient-to-br from-[#052016] via-[#081c15] to-[#1b4332]",
  role: "bg-gradient-to-br from-[#081c15] via-[#1b4332] to-[#52b788]",
  forgot: "bg-gradient-to-br from-[#081c15] via-[#1b4332] to-[#344e41]",
};

export function AuthSplitLayout({
  children,
  panelTitle,
  panelSubtitle,
  panelTone = "login",
  wide = false,
}: AuthSplitLayoutProps) {
  return (
    <div className="auth-shell grid min-h-screen xl:grid-cols-[minmax(320px,42%)_1fr]">
      <aside
        className={`relative hidden overflow-hidden text-white lg:flex lg:flex-col lg:justify-between ${panelArt[panelTone]} p-10 xl:p-12`}
      >
        <div className="pointer-events-none absolute inset-0 opacity-40">
          <div className="absolute -left-10 top-24 h-56 w-56 rounded-full bg-lime-300/15 blur-2xl" />
          <div className="absolute -right-8 bottom-10 h-64 w-64 rounded-full bg-emerald-400/10 blur-3xl" />
        </div>

        <div className="relative z-10">
          <Link
            href="/"
            className="inline-flex items-center gap-2.5 text-lg font-semibold tracking-tight text-white"
          >
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/15 text-lime-300">
              <Leaf className="h-5 w-5" strokeWidth={2.25} aria-hidden />
            </span>
            AgriTwin AI
          </Link>
        </div>

        <div className="relative z-10 max-w-lg space-y-4 pb-8">
          <AuthFieldVisual />
          <h2 className="text-3xl font-semibold leading-tight text-white xl:text-4xl">
            {panelTitle}
          </h2>
          <p className="text-base text-white/85 xl:text-lg">{panelSubtitle}</p>
        </div>

        <p className="relative z-10 text-xs text-white/65">
          Toprak nemi ve sulama karar desteği
        </p>
      </aside>

      <div className="flex flex-col bg-[var(--auth-bg)]">
        <div className="flex items-center justify-between px-5 py-4 lg:hidden">
          <Link
            href="/"
            className="inline-flex items-center gap-2 font-semibold text-[var(--auth-forest)]"
          >
            <Leaf className="h-5 w-5 text-emerald-600" aria-hidden />
            AgriTwin AI
          </Link>
        </div>
        <div className="flex flex-1 items-center justify-center px-5 py-8 sm:px-10 lg:px-14">
          <div className={`w-full ${wide ? "max-w-2xl" : "max-w-lg"}`}>{children}</div>
        </div>
        <div className="auth-mobile-footer border-t border-[var(--auth-border)] px-5 py-4 text-center text-xs text-[var(--auth-muted)] lg:hidden">
          Akıllı tarım · güvenli giriş
        </div>
      </div>
    </div>
  );
}
