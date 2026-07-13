"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";
import { api, clearSession, getStoredUser, setSession, User } from "@/lib/api";

const NAV = [
  { href: "/admin", label: "Genel Bakış", exact: true },
  { href: "/admin/users", label: "Kullanıcılar" },
  { href: "/admin/farms", label: "Çiftlikler" },
  { href: "/admin/devices", label: "Cihaz filosu" },
  { href: "/admin/billing", label: "Abonelik" },
  { href: "/admin/support", label: "Destek" },
  { href: "/admin/analytics", label: "Raporlar" },
  { href: "/admin/settings", label: "Ayarlar" },
];

export function AdminShell({
  children,
  title,
}: {
  children: ReactNode;
  title: string;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [error, setError] = useState("");
  const [bootstrapping, setBootstrapping] = useState(false);

  useEffect(() => {
    const stored = getStoredUser();
    if (!stored) {
      router.replace("/login");
      return;
    }
    setUser(stored);
  }, [router, pathname]);

  const isAdmin =
    user?.role === "admin" || user?.role === "super_admin";

  async function becomeAdmin() {
    setBootstrapping(true);
    setError("");
    try {
      const u = await api.adminBootstrap();
      const token = localStorage.getItem("agritwin_token");
      if (token) setSession(token, u);
      setUser(u);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Yetki alınamadı");
    } finally {
      setBootstrapping(false);
    }
  }

  function logout() {
    clearSession();
    router.push("/login");
  }

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-[var(--auth-muted)]">
        Yükleniyor…
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center gap-4 px-4">
        <h1 className="text-xl font-bold">Yönetim paneli</h1>
        <p className="text-sm text-[var(--auth-muted)]">
          Bu alan yalnızca yöneticiler içindir. Henüz admin yoksa bu hesap ile
          bootstrap yapabilirsiniz.
        </p>
        {error && <p className="text-sm text-red-700">{error}</p>}
        <button
          type="button"
          className="btn btn-primary"
          disabled={bootstrapping}
          onClick={becomeAdmin}
        >
          {bootstrapping ? "…" : "Bu hesabı yönetici yap"}
        </button>
        <Link href="/dashboard" className="btn btn-secondary text-center">
          Çiftçi paneline dön
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--app-bg)] text-[var(--auth-ink)]">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-60 flex-col bg-[var(--auth-forest)] text-white lg:flex">
        <Link href="/admin" className="px-4 py-5 text-lg font-semibold">
          AgriTwin AI · Admin
        </Link>
        <nav className="flex flex-1 flex-col gap-0.5 px-2">
          {NAV.map((item) => {
            const active = item.exact
              ? pathname === item.href
              : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-lg px-3 py-2.5 text-sm ${
                  active ? "bg-white/15 font-semibold" : "text-white/75 hover:bg-white/10"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-white/15 p-4 text-xs">
          <p className="font-semibold">{user.name}</p>
          <p className="text-white/70">{user.role}</p>
          <button type="button" className="mt-2 underline" onClick={logout}>
            Çıkış
          </button>
        </div>
      </aside>

      <div className="lg:pl-60">
        <header className="sticky top-0 z-30 flex items-center justify-between gap-3 border-b border-[var(--auth-border)] bg-white/95 px-4 py-3 backdrop-blur">
          <div className="flex items-center gap-2">
            <button
              type="button"
              className="btn btn-ghost px-2 lg:hidden"
              onClick={() => setMenuOpen((v) => !v)}
            >
              Menü
            </button>
            <h1 className="text-lg font-semibold">{title}</h1>
          </div>
          <Link href="/dashboard" className="text-xs text-[var(--auth-forest)] hover:underline">
            Çiftçi app
          </Link>
        </header>

        {menuOpen && (
          <nav className="border-b border-[var(--auth-border)] bg-white px-2 py-2 lg:hidden">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMenuOpen(false)}
                className="block rounded-lg px-3 py-2 text-sm"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        )}

        <main className="px-4 py-5 pb-24 sm:px-6">{children}</main>

        <nav className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-4 border-t border-[var(--auth-border)] bg-white lg:hidden">
          {[
            { href: "/admin", label: "Özet" },
            { href: "/admin/farms", label: "Çiftlik" },
            { href: "/admin/devices", label: "Cihaz" },
            { href: "/admin/support", label: "Diğer" },
          ].map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`py-3 text-center text-[10px] font-medium ${
                pathname.startsWith(item.href) && !(item.href === "/admin" && pathname !== "/admin")
                  ? "text-[var(--auth-forest)]"
                  : item.href === "/admin" && pathname === "/admin"
                    ? "text-[var(--auth-forest)]"
                    : "text-[var(--auth-muted)]"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </div>
  );
}
