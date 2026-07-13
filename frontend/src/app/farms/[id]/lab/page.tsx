"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app/AppShell";
import { FarmSelector, setSelectedFarmId } from "@/components/app/FarmSelector";
import { KpiCard } from "@/components/app/KpiCard";
import { api, Farm, LabReport, LabSummary } from "@/lib/api";

function statusLabel(s?: string | null) {
  if (s === "verified") return "Doğrulandı";
  if (s === "pending") return "Bekliyor";
  if (s === "missing") return "Eksik";
  return s || "—";
}

function statusTone(s?: string | null) {
  if (s === "verified") return "bg-emerald-100 text-emerald-800";
  if (s === "pending") return "bg-amber-100 text-amber-900";
  if (s === "missing") return "bg-red-100 text-red-800";
  return "bg-slate-100 text-slate-700";
}

export default function LabListPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [reports, setReports] = useState<LabReport[]>([]);
  const [summary, setSummary] = useState<LabSummary | null>(null);
  const [filter, setFilter] = useState<"all" | "verified" | "pending" | "missing">(
    "all",
  );
  const [error, setError] = useState("");

  async function load() {
    const [f, list, sum] = await Promise.all([
      api.getFarm(farmId),
      api.listLabReports(farmId, {
        status: filter === "all" ? undefined : filter,
      }),
      api.labSummary(farmId),
    ]);
    setFarm(f);
    setReports(list);
    setSummary(sum);
  }

  useEffect(() => {
    if (!farmId) return;
    setSelectedFarmId(farmId);
    load().catch((err) => setError(err.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [farmId, filter]);

  return (
    <AppShell title="Laboratuvar Analizleri" farmName={farm?.name}>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <FarmSelector farmId={farmId} suffixPath="/lab" />
        <span className="rounded-full bg-violet-100 px-2 py-0.5 text-[10px] font-bold text-violet-900">
          Lab ≠ IoT sensör
        </span>
        <Link
          href={`/farms/${farmId}/lab/new`}
          className="btn btn-primary ml-auto hidden text-sm lg:inline-flex"
        >
          + Rapor yükle
        </Link>
      </div>

      {error && (
        <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>
      )}

      <div className="mb-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard label="Toplam analiz" value={String(summary?.total ?? "—")} />
        <KpiCard
          label="Onay bekleyen"
          value={String(summary?.pending ?? "—")}
          tone={summary && summary.pending > 0 ? "warn" : undefined}
        />
        <KpiCard
          label="Son 30 gün"
          value={String(summary?.last_30_days ?? "—")}
          tone="ok"
        />
        <KpiCard
          label="Kritik bulgu"
          value={String(summary?.critical_findings ?? "—")}
          tone={
            summary && summary.critical_findings > 0 ? "warn" : undefined
          }
        />
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {(
          [
            ["all", "Tümü"],
            ["verified", "Doğrulandı"],
            ["pending", "Bekliyor"],
            ["missing", "Eksik"],
          ] as const
        ).map(([key, label]) => (
          <button
            key={key}
            type="button"
            onClick={() => setFilter(key)}
            className={`rounded-full px-3 py-1.5 text-xs font-semibold ${
              filter === key
                ? "bg-[var(--auth-forest)] text-white"
                : "bg-white text-[var(--auth-muted)] ring-1 ring-[var(--auth-border)]"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <ul className="space-y-3 lg:hidden">
        {reports.map((r) => (
          <li key={r.id}>
            <Link
              href={
                r.status === "pending" || r.status === "missing"
                  ? `/farms/${farmId}/lab/${r.id}/verify`
                  : `/farms/${farmId}/lab/${r.id}`
              }
              className="app-surface block p-4"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="font-semibold">
                    {r.report_number || `Rapor #${r.id}`}
                  </p>
                  <p className="text-xs text-[var(--auth-muted)]">
                    {r.lab_name}
                    {r.sample_region ? ` · ${r.sample_region}` : ""}
                  </p>
                </div>
                <span
                  className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${statusTone(r.status)}`}
                >
                  {statusLabel(r.status)}
                </span>
              </div>
              <p className="mt-2 text-xs text-[var(--auth-muted)]">
                pH {r.ph ?? "—"} · EC {r.ec ?? "—"} · OM {r.om ?? "—"}%
              </p>
            </Link>
          </li>
        ))}
        {reports.length === 0 && (
          <li className="rounded-2xl border border-dashed border-[var(--auth-border)] p-8 text-center text-sm text-[var(--auth-muted)]">
            Henüz laboratuvar raporu yok.
          </li>
        )}
      </ul>

      <div className="app-surface hidden overflow-x-auto lg:block">
        <table className="w-full min-w-[800px] text-left text-sm">
          <thead className="border-b border-[var(--auth-border)] text-xs text-[var(--auth-muted)]">
            <tr>
              <th className="px-4 py-3 font-medium">Rapor</th>
              <th className="px-4 py-3 font-medium">Bölge</th>
              <th className="px-4 py-3 font-medium">Tarih</th>
              <th className="px-4 py-3 font-medium">Lab</th>
              <th className="px-4 py-3 font-medium">pH</th>
              <th className="px-4 py-3 font-medium">EC</th>
              <th className="px-4 py-3 font-medium">OM %</th>
              <th className="px-4 py-3 font-medium">Durum</th>
              <th className="px-4 py-3 font-medium" />
            </tr>
          </thead>
          <tbody>
            {reports.map((r) => (
              <tr
                key={r.id}
                className="border-b border-[var(--auth-border)] last:border-0"
              >
                <td className="px-4 py-3 font-medium">
                  {r.report_number || `#${r.id}`}
                </td>
                <td className="px-4 py-3">{r.sample_region || "—"}</td>
                <td className="px-4 py-3">
                  {r.sample_date
                    ? new Date(r.sample_date).toLocaleDateString("tr-TR")
                    : new Date(r.created_at).toLocaleDateString("tr-TR")}
                </td>
                <td className="px-4 py-3">{r.lab_name}</td>
                <td className="px-4 py-3">{r.ph ?? "—"}</td>
                <td className="px-4 py-3">{r.ec ?? "—"}</td>
                <td className="px-4 py-3">{r.om ?? "—"}</td>
                <td className="px-4 py-3">
                  <span
                    className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${statusTone(r.status)}`}
                  >
                    {statusLabel(r.status)}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <Link
                    href={`/farms/${farmId}/lab/${r.id}`}
                    className="text-[var(--auth-forest)] hover:underline"
                  >
                    Detay
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {reports.length === 0 && (
          <p className="p-8 text-center text-sm text-[var(--auth-muted)]">
            Henüz rapor yok.
          </p>
        )}
      </div>

      <p className="mt-4 text-xs text-[var(--auth-muted)]">
        Laboratuvar analizi toprak profili kaydıdır; canlı nem/IoT verisinin
        yerine geçmez.
      </p>

      <Link
        href={`/farms/${farmId}/lab/new`}
        className="fixed bottom-20 right-4 z-30 flex items-center gap-2 rounded-full bg-[var(--auth-forest)] px-4 py-3 text-sm font-semibold text-white shadow-lg lg:hidden"
      >
        + Rapor
      </Link>
    </AppShell>
  );
}
