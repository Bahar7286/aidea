"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";
import {
  Activity,
  BrainCircuit,
  Droplets,
  FlaskConical,
  LayoutDashboard,
  Leaf,
  Map,
  MapPinned,
  Menu,
  Plus,
  Radio,
  Settings2,
  Sprout,
} from "lucide-react";
import {
  getSelectedFarmId,
  setSelectedFarmId,
} from "@/components/app/FarmSelector";
import { api, clearSession, getStoredUser, User } from "@/lib/api";

type Props = {
  children: ReactNode;
  title?: string;
  farmName?: string;
};

type NavItem = {
  href: string;
  label: string;
  active: boolean;
  needsFarm?: boolean;
  icon: typeof LayoutDashboard;
};

function farmIdFromPath(pathname: string): number | null {
  const m = pathname.match(/^\/farms\/(\d+)(?:\/|$)/);
  if (!m) return null;
  const n = Number(m[1]);
  return Number.isFinite(n) && n > 0 ? n : null;
}

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

    const fromPath = farmIdFromPath(pathname);
    if (fromPath) {
      setSelectedFarmId(fromPath);
      setFarmId(fromPath);
      return;
    }

    const saved = getSelectedFarmId();
    if (saved) {
      setFarmId(saved);
      return;
    }

    let cancelled = false;
    api
      .listFarms()
      .then((rows) => {
        if (cancelled || !rows[0]) return;
        setSelectedFarmId(rows[0].id);
        setFarmId(rows[0].id);
      })
      .catch(() => {
        /* nav falls back to /farms */
      });
    return () => {
      cancelled = true;
    };
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

  const DESKTOP_NAV: NavItem[] = [
    {
      href: "/dashboard",
      label: "Genel Bakış",
      active: pathname === "/dashboard",
      icon: LayoutDashboard,
    },
    {
      href: "/farms",
      label: "Araziler",
      active: pathname === "/farms" || pathname === "/farms/new",
      icon: MapPinned,
    },
    {
      href: `${farmBase}/twin`,
      label: "Dijital İkiz",
      active: pathname.includes("/twin"),
      needsFarm: true,
      icon: Map,
    },
    {
      href: `${farmBase}/devices`,
      label: "Cihazlar",
      active: pathname.includes("/devices"),
      needsFarm: true,
      icon: Radio,
    },
    {
      href: `${farmBase}/sensors/live`,
      label: "Sensörler",
      active: pathname.includes("/sensors"),
      needsFarm: true,
      icon: Activity,
    },
    {
      href: `${farmBase}/lab`,
      label: "Laboratuvar",
      active: pathname.includes("/lab"),
      needsFarm: true,
      icon: FlaskConical,
    },
    {
      href: `${farmBase}/ai`,
      label: "AI Önerileri",
      active: pathname.includes("/ai"),
      needsFarm: true,
      icon: BrainCircuit,
    },
    {
      href: `${farmBase}/irrigation`,
      label: "Sulama",
      active:
        pathname.includes("/irrigation") || pathname.includes("/scenarios"),
      needsFarm: true,
      icon: Droplets,
    },
    {
      href: `${farmBase}/hub`,
      label: "Raporlar / Ayarlar",
      active: pathname.includes("/hub"),
      needsFarm: true,
      icon: Settings2,
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
      icon: Sprout,
    },
  ];

  const mobileNav = [
    {
      href: "/dashboard",
      label: "Ana Sayfa",
      active: pathname === "/dashboard",
      icon: LayoutDashboard,
    },
    {
      href: "/farms",
      label: "Araziler",
      active: pathname === "/farms" || pathname.includes("/edit"),
      icon: MapPinned,
    },
    {
      href: farmId ? `/farms/${farmId}/sensors/live` : "/farms",
      label: "Sensör",
      active: pathname.includes("/sensors"),
      icon: Activity,
    },
    {
      href: farmId ? `/farms/${farmId}/ai` : "/farms",
      label: "AI",
      active: pathname.includes("/ai"),
      icon: BrainCircuit,
    },
    {
      href: farmId ? `/farms/${farmId}/hub` : "/farms",
      label: "Diğer",
      active:
        pathname.includes("/hub") ||
        pathname.includes("/irrigation") ||
        pathname.includes("/lab"),
      icon: Menu,
    },
  ];

  return (
    <div className="app-shell min-h-screen bg-[var(--app-bg)] text-[var(--auth-ink)]">
      <aside className="app-sidebar hidden lg:flex">
        <Link href="/dashboard" className="flex items-center gap-2.5 px-1 py-1 font-semibold">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--auth-forest)] text-lime-300 shadow-sm">
            <Leaf className="h-5 w-5" strokeWidth={2.25} aria-hidden />
          </span>
          AgriTwin AI
        </Link>
        <nav className="mt-8 flex flex-1 flex-col gap-0.5">
          {DESKTOP_NAV.map((item) => {
            const href = item.needsFarm && !farmId ? "/farms" : item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.label}
                href={href}
                prefetch
                className={`flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                  item.active
                    ? "bg-[var(--auth-forest)] text-white shadow-sm"
                    : "text-[var(--auth-muted)] hover:bg-emerald-50 hover:text-[var(--auth-ink)]"
                }`}
              >
                <Icon
                  className={`h-[18px] w-[18px] shrink-0 ${
                    item.active ? "text-lime-300" : "text-emerald-700/80"
                  }`}
                  strokeWidth={2.25}
                  aria-hidden
                />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <Link href="/farms/new" className="btn btn-primary mt-4 w-full text-sm">
          <Plus className="h-4 w-4" aria-hidden />
          Hızlı İşlem
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

      <div className="app-main flex min-h-screen flex-col lg:pl-[260px]">
        <header className="sticky top-0 z-30 border-b border-[var(--auth-border)] bg-white/95 backdrop-blur">
          <div className="app-content flex items-center justify-between gap-3 py-3">
            <div className="min-w-0">
              <p className="truncate text-lg font-semibold">{title || "Genel Bakış"}</p>
              {farmName && (
                <p className="truncate text-xs text-[var(--auth-muted)]">{farmName}</p>
              )}
            </div>
            <div className="flex items-center gap-2 sm:gap-3">
              <span className="hidden items-center gap-1.5 rounded-full bg-emerald-100 px-2.5 py-1 text-[10px] font-bold text-emerald-800 sm:inline-flex">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-600" />
                Simüle IoT
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

        <main className="app-content flex-1 py-5 pb-24 lg:pb-8">{children}</main>

        <nav className="fixed inset-x-0 bottom-0 z-40 border-t border-[var(--auth-border)] bg-white lg:hidden">
          <ul className="grid grid-cols-5">
            {mobileNav.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.label}>
                  <Link
                    href={item.href}
                    prefetch
                    className={`flex flex-col items-center gap-0.5 px-1 py-2 text-[10px] font-medium ${
                      item.active
                        ? "text-[var(--auth-forest)]"
                        : "text-[var(--auth-muted)]"
                    }`}
                  >
                    <Icon
                      className={`h-5 w-5 ${
                        item.active ? "text-emerald-600" : "text-slate-400"
                      }`}
                      strokeWidth={item.active ? 2.4 : 2}
                      aria-hidden
                    />
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </div>
    </div>
  );
}
