"use client";

import Link from "next/link";
import { ReactNode } from "react";
import { Leaf } from "lucide-react";

type AuthSplitLayoutProps = {
  children: ReactNode;
  panelTitle: string;
  panelSubtitle: string;
  panelTone?: "login" | "register" | "verify" | "role" | "forgot";
  /** Wider form column for role / multi-field screens */
  wide?: boolean;
};

const panelArt: Record<string, string> = {
  login: "from-[#1b4332] via-[#2d6a4f] to-[#40916c]",
  register: "from-[#1b4332] via-[#2d6a4f] to-[#52b788]",
  verify: "from-[#081c15] via-[#1b4332] to-[#2d6a4f]",
  role: "from-[#1b4332] via-[#2d6a4f] to-[#74c69d]",
  forgot: "from-[#1b4332] via-[#344e41] to-[#588157]",
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
        <div className="relative z-10">
          <Link href="/" className="inline-flex items-center gap-2.5 text-lg font-semibold tracking-tight">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/15 text-lime-300">
              <Leaf className="h-5 w-5" strokeWidth={2.25} aria-hidden />
            </span>
            AgriTwin AI
          </Link>
        </div>
        <div className="relative z-10 max-w-lg space-y-4 pb-8">
          <div className="auth-panel-illustration mb-6 h-44 rounded-2xl bg-white/10 backdrop-blur-sm" />
          <h2 className="text-3xl font-semibold leading-tight xl:text-4xl">{panelTitle}</h2>
          <p className="text-base text-white/85 xl:text-lg">{panelSubtitle}</p>
        </div>
        <p className="relative z-10 text-xs text-white/60">
          Toprak nemi ve sulama karar desteği — sınırlı dijital ikiz prototipi
        </p>
        <div className="pointer-events-none absolute -right-16 -bottom-16 h-64 w-64 rounded-full bg-white/10" />
        <div className="pointer-events-none absolute right-20 top-24 h-32 w-32 rounded-full bg-lime-300/20" />
      </aside>

      <div className="flex flex-col bg-[var(--auth-bg)]">
        <div className="flex items-center justify-between px-5 py-4 lg:hidden">
          <Link href="/" className="inline-flex items-center gap-2 font-semibold text-[var(--auth-forest)]">
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
