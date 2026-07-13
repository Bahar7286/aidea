"use client";

import Link from "next/link";
import { ReactNode } from "react";

type AuthSplitLayoutProps = {
  children: ReactNode;
  panelTitle: string;
  panelSubtitle: string;
  panelTone?: "login" | "register" | "verify" | "role" | "forgot";
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
}: AuthSplitLayoutProps) {
  return (
    <div className="auth-shell grid min-h-screen lg:grid-cols-2">
      <aside
        className={`relative hidden overflow-hidden text-white lg:flex lg:flex-col lg:justify-between ${panelArt[panelTone]} p-10`}
      >
        <div className="relative z-10">
          <Link href="/" className="inline-flex items-center gap-2 text-lg font-semibold tracking-tight">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-white/15">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
                <path
                  d="M12 3c4 4 6 7 6 10a6 6 0 1 1-12 0c0-3 2-6 6-10Z"
                  fill="currentColor"
                />
              </svg>
            </span>
            AgriTwin AI
          </Link>
        </div>
        <div className="relative z-10 max-w-md space-y-4 pb-8">
          <div className="auth-panel-illustration mb-6 h-40 rounded-2xl bg-white/10 backdrop-blur-sm" />
          <h2 className="text-3xl font-semibold leading-tight">{panelTitle}</h2>
          <p className="text-base text-white/85">{panelSubtitle}</p>
        </div>
        <p className="relative z-10 text-xs text-white/60">
          Toprak nemi ve sulama karar desteği — sınırlı dijital ikiz prototipi
        </p>
        <div className="pointer-events-none absolute -right-16 -bottom-16 h-64 w-64 rounded-full bg-white/10" />
        <div className="pointer-events-none absolute right-20 top-24 h-32 w-32 rounded-full bg-lime-300/20" />
      </aside>

      <div className="flex flex-col bg-[var(--auth-bg)]">
        <div className="flex items-center justify-between px-5 py-4 lg:hidden">
          <Link href="/" className="font-semibold text-[var(--auth-forest)]">
            AgriTwin AI
          </Link>
        </div>
        <div className="flex flex-1 items-center justify-center px-5 py-8 sm:px-10">
          <div className="w-full max-w-md">{children}</div>
        </div>
        <div className="auth-mobile-footer border-t border-[var(--auth-border)] px-5 py-4 text-center text-xs text-[var(--auth-muted)] lg:hidden">
          Akıllı tarım · güvenli giriş
        </div>
      </div>
    </div>
  );
}
