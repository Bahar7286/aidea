"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";
import { getSelectedFarmId } from "@/components/app/FarmSelector";
import { clearSession, getStoredUser, User } from "@/lib/api";

type Props = {
  children: ReactNode;
  title?: string;
  farmName?: string;
};

export function AppShell({ children, title, farmName }: Props) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [farmId, setFarmId] = useState<number | null>(null);

  useEffect(() => {
    const stored = getStoredUser();
    if (!stored) {
      router.replace("/login");
      return;
    }
    setUser(stored);
    setFarmId(getSelectedFarmId());
  }, [router, pathname]);

  function logout() {
    clearSession();
    router.push("/login");
  }

  const dateLabel = new Date().toLocaleDateString("tr-TR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const farmBase = farmId ? `/farms/${farmId}` : "/farms";

  const DESKTOP_NAV = [
    { href: "/dashboard", label: "Genel Bakış", active: pathname === "/dashboard" },
    {
      href: "/farms",
      label: "Araziler",
      active: pathname === "/farms" || pathname === "/farms/new",
    },
    {
      href: `${farmBase}/twin`,
      label: "Dijital İkiz",
      active: pathname.includes("/twin"),
      needsFarm: true,
    },
    {
      href: `${farmBase}/devices`,
      label: "Cihazlar",
      active: pathname.includes("/devices"),
      needsFarm: true,
    },
    {
      href: `${farmBase}/sensors/live`,
      label: "Sensörler",
      active: pathname.includes("/sensors"),
      needsFarm: true,
    },
    {
      href: `${farmBase}/lab`,
      label: "Laboratuvar",
      active: pathname.includes("/lab"),
      needsFarm: true,
    },
    {
      href: `${farmBase}/ai`,
      label: "AI Önerileri",
      active: pathname.includes("/ai"),
      needsFarm: true,
    },
    {
      href: `${farmBase}/irrigation`,
      label: "Sulama",
      active:
        pathname.includes("/irrigation") || pathname.includes("/scenarios"),
      needsFarm: true,
    },
    {
      href: `${farmBase}/hub`,
      label: "Raporlar / Ayarlar",
      active: pathname.includes("/hub"),
      needsFarm: true,
    },
    {
      href: farmBase,
      label: "Arazi detay",
      active:
        pathname.match(/\/farms\/\d+$/) != null &&
        !pathname.includes("/twin") &&
        !pathname.includes("/sensors") &&
        !pathname.includes("/data") &&
        !pathname.includes("/devices") &&
        !pathname.includes("/lab") &&
        !pathname.includes("/ai") &&
        !pathname.includes("/irrigation") &&
        !pathname.includes("/scenarios") &&
        !pathname.includes("/hub") &&
        !pathname.includes("/zones") &&
        !pathname.includes("/edit"),
      needsFarm: true,
    },
  ];

  return (
    <div className="app-shell min-h-screen bg-[var(--app-bg)] text-[var(--auth-ink)]">
      <aside className="app-sidebar hidden lg:flex">
        <Link href="/dashboard" className="flex items-center gap-2 px-1 py-1 font-semibold">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--auth-forest)] text-white">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
              <path d="M12 3c4 4 6 7 6 10a6 6 0 1 1-12 0c0-3 2-6 6-10Z" />
            </svg>
          </span>
          AgriTwin AI
        </Link>
        <nav className="mt-8 flex flex-1 flex-col gap-1">
          {DESKTOP_NAV.map((item) => {
            const href =
              item.needsFarm && !farmId ? "/farms" : item.href;
            return (
              <Link
                key={item.label}
                href={href}
                className={`rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                  item.active
                    ? "bg-[var(--auth-forest)] text-white"
                    : "text-[var(--auth-muted)] hover:bg-black/5 hover:text-[var(--auth-ink)]"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        <Link href="/farms/new" className="btn btn-primary mt-4 w-full text-sm">
          + Hızlı İşlem
        </Link>
        <div className="mt-4 border-t border-[var(--auth-border)] pt-3 text-xs">
          <p className="font-semibold">{user?.name || "…"}</p>
          <p className="text-[var(--auth-muted)]">{user?.role}</p>
          <Link
            href="/admin"
            className="mt-2 block text-[var(--auth-forest)] hover:underline"
          >
            Yönetim paneli
          </Link>
        </div>
      </aside>

      <div className="app-main flex min-h-screen flex-col lg:pl-[240px]">
        <header className="sticky top-0 z-30 border-b border-[var(--auth-border)] bg-white/95 backdrop-blur">
          <div className="flex items-center justify-between gap-3 px-4 py-3 sm:px-6">
            <div className="min-w-0">
              <p className="truncate text-lg font-semibold">{title || "Genel Bakış"}</p>
              {farmName && (
                <p className="truncate text-xs text-[var(--auth-muted)]">{farmName}</p>
              )}
            </div>
            <div className="flex items-center gap-2 sm:gap-3">
              <span className="hidden items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800 sm:inline-flex">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-600" />
                Canlı
              </span>
              <span className="hidden text-xs text-[var(--auth-muted)] md:inline">
                {dateLabel}
              </span>
              <button
                type="button"
                className="btn btn-secondary px-3 text-xs"
                onClick={logout}
              >
                Çıkış
              </button>
            </div>
          </div>
        </header>

        <main className="flex-1 px-4 py-5 pb-24 sm:px-6 lg:pb-8">{children}</main>

        <nav className="fixed inset-x-0 bottom-0 z-40 border-t border-[var(--auth-border)] bg-white lg:hidden">
          <ul className="grid grid-cols-5">
            {[
              {
                href: "/dashboard",
                label: "Ana Sayfa",
                active: pathname === "/dashboard",
              },
              {
                href: "/farms",
                label: "Araziler",
                active: pathname === "/farms" || pathname.includes("/edit"),
              },
              {
                href: farmId ? `/farms/${farmId}/sensors/live` : "/farms",
                label: "Sensör",
                active: pathname.includes("/sensors"),
              },
              {
                href: farmId ? `/farms/${farmId}/ai` : "/farms",
                label: "AI",
                active: pathname.includes("/ai"),
              },
              {
                href: farmId ? `/farms/${farmId}/hub` : "/farms",
                label: "Diğer",
                active:
                  pathname.includes("/hub") ||
                  pathname.includes("/irrigation") ||
                  pathname.includes("/lab"),
              },
            ].map((item) => (
              <li key={item.label}>
                <Link
                  href={item.href}
                  className={`flex flex-col items-center gap-0.5 px-1 py-2.5 text-[10px] font-medium ${
                    item.active
                      ? "text-[var(--auth-forest)]"
                      : "text-[var(--auth-muted)]"
                  }`}
                >
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      item.active ? "bg-[var(--auth-forest)]" : "bg-transparent"
                    }`}
                  />
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </div>
  );
}
