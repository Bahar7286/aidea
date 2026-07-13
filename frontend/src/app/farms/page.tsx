"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/app/AppShell";
import { api, Farm } from "@/lib/api";

export default function FarmsPage() {
  const [farms, setFarms] = useState<Farm[]>([]);
  const [q, setQ] = useState("");
  const [filter, setFilter] = useState<"all" | "active" | "passive">("all");
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listFarms(true)
      .then(setFarms)
      .catch((err) => setError(err.message));
  }, []);

  const filtered = useMemo(() => {
    return farms.filter((f) => {
      const active = f.is_active !== false;
      if (filter === "active" && !active) return false;
      if (filter === "passive" && active) return false;
      if (!q.trim()) return true;
      const hay = `${f.name} ${f.location || ""} ${f.crops[0]?.crop_type || ""}`.toLowerCase();
      return hay.includes(q.toLowerCase());
    });
  }, [farms, filter, q]);

  return (
    <AppShell title="Arazilerim">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <input
          className="input max-w-md"
          placeholder="Arazi ara..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <Link href="/farms/new" className="btn btn-primary">
          + Yeni Arazi Ekle
        </Link>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {(
          [
            ["all", "Tümü"],
            ["active", "Aktif"],
            ["passive", "Pasif"],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            onClick={() => setFilter(id)}
            className={`rounded-full px-3 py-1.5 text-xs font-semibold ${
              filter === id
                ? "bg-[var(--auth-forest)] text-white"
                : "bg-white text-[var(--auth-muted)] ring-1 ring-[var(--auth-border)]"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {error && <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>}

      {/* Mobile cards */}
      <div className="space-y-3 lg:hidden">
        {filtered.map((f) => (
          <div key={f.id} className="app-surface p-4">
            <div className="flex items-start justify-between gap-2">
              <div>
                <Link
                  href={`/farms/${f.id}`}
                  className="font-semibold text-[var(--auth-ink)]"
                >
                  {f.name}
                </Link>
                <p className="text-xs text-[var(--auth-muted)]">
                  {f.location || "Konum yok"} · {f.area ?? "—"} da ·{" "}
                  {f.crops[0]?.crop_type || "ürün yok"}
                </p>
              </div>
              <span
                className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                  f.is_active !== false
                    ? "bg-emerald-100 text-emerald-800"
                    : "bg-slate-100 text-slate-600"
                }`}
              >
                {f.is_active !== false ? "Aktif" : "Pasif"}
              </span>
            </div>
            <div className="mt-3 flex gap-2">
              <Link href={`/farms/${f.id}`} className="btn btn-secondary flex-1 text-xs">
                Görüntüle
              </Link>
              <Link
                href={`/farms/${f.id}/edit`}
                className="btn btn-ghost text-xs"
              >
                Düzenle
              </Link>
            </div>
          </div>
        ))}
        {filtered.length === 0 && (
          <p className="text-sm text-[var(--auth-muted)]">Arazi bulunamadı.</p>
        )}
      </div>

      {/* Desktop table */}
      <div className="app-surface hidden overflow-x-auto lg:block">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead>
            <tr className="border-b border-[var(--auth-border)] text-[var(--auth-muted)]">
              <th className="px-4 py-3 font-medium">Arazi</th>
              <th className="px-4 py-3 font-medium">Konum</th>
              <th className="px-4 py-3 font-medium">Ürün</th>
              <th className="px-4 py-3 font-medium">Alan</th>
              <th className="px-4 py-3 font-medium">Toprak</th>
              <th className="px-4 py-3 font-medium">Sensör</th>
              <th className="px-4 py-3 font-medium">Durum</th>
              <th className="px-4 py-3 font-medium">İşlem</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((f) => (
              <tr key={f.id} className="border-b border-[var(--auth-border)]">
                <td className="px-4 py-3 font-semibold">
                  <Link href={`/farms/${f.id}`} className="hover:underline">
                    {f.name}
                  </Link>
                </td>
                <td className="px-4 py-3 text-[var(--auth-muted)]">
                  {f.location || "—"}
                </td>
                <td className="px-4 py-3">{f.crops[0]?.crop_type || "—"}</td>
                <td className="px-4 py-3">{f.area ?? "—"} da</td>
                <td className="px-4 py-3">{f.soil_type || "—"}</td>
                <td className="px-4 py-3">{f.device_count ?? 0}</td>
                <td className="px-4 py-3">
                  <span
                    className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                      f.is_active !== false
                        ? "bg-emerald-100 text-emerald-800"
                        : "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {f.is_active !== false ? "Aktif" : "Pasif"}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <Link
                      href={`/farms/${f.id}`}
                      className="text-[var(--auth-forest)] hover:underline"
                    >
                      Gör
                    </Link>
                    <Link
                      href={`/farms/${f.id}/edit`}
                      className="text-[var(--auth-muted)] hover:underline"
                    >
                      Düzenle
                    </Link>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <p className="p-4 text-sm text-[var(--auth-muted)]">Arazi bulunamadı.</p>
        )}
      </div>

      <Link
        href="/farms/new"
        className="fixed bottom-20 right-4 z-30 flex h-14 w-14 items-center justify-center rounded-full bg-[var(--auth-forest)] text-2xl text-white shadow-lg lg:hidden"
        aria-label="Yeni arazi"
      >
        +
      </Link>
    </AppShell>
  );
}
