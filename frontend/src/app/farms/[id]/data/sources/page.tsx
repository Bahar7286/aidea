"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/app/AppShell";
import { FarmSelector, setSelectedFarmId } from "@/components/app/FarmSelector";
import { api, DataSource, Farm } from "@/lib/api";

const actions: Record<string, { href: string; label: string }> = {
  manual: { href: "data/manual", label: "Veri gir" },
  simulation: { href: "sensors/live", label: "Simüle et" },
  test_dataset: { href: "sensors/live", label: "Senaryo" },
  iot: { href: "sensors/live", label: "Canlı" },
  lab: { href: "lab", label: "Lab raporları" },
  devices: { href: "devices", label: "Cihazlar" },
};

export default function DataSourcesPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [sources, setSources] = useState<DataSource[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!farmId) return;
    setSelectedFarmId(farmId);
    Promise.all([api.getFarm(farmId), api.dataSources(farmId)])
      .then(([f, s]) => {
        setFarm(f);
        setSources(s);
      })
      .catch((err) => setError(err.message));
  }, [farmId]);

  const active = sources.filter((s) => s.status === "active").length;

  return (
    <AppShell title="Veri Kaynakları Merkezi" farmName={farm?.name}>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <FarmSelector farmId={farmId} suffixPath="/data/sources" />
        <Link href={`/farms/${farmId}/data/manual`} className="btn btn-primary text-sm">
          + Yeni kaynak / manuel
        </Link>
      </div>

      {error && <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>}

      <p className="mb-4 text-sm text-[var(--auth-muted)]">
        {sources.length} kaynak · {active} aktif · Simülasyon asla “gerçek sensör”
        diye sunulmaz.
      </p>

      {/* Mobile cards */}
      <div className="space-y-3 lg:hidden">
        {sources.map((s) => {
          const act = actions[s.key] || actions.manual;
          return (
            <div key={s.key} className="app-surface p-4">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="font-semibold">{s.name}</p>
                  <p className="text-xs text-[var(--auth-muted)]">{s.source_type}</p>
                </div>
                <span
                  className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                    s.status === "active"
                      ? "bg-emerald-100 text-emerald-800"
                      : s.status === "pending"
                        ? "bg-amber-100 text-amber-800"
                        : "bg-slate-100 text-slate-600"
                  }`}
                >
                  {s.status}
                </span>
              </div>
              <p className="mt-2 text-xs text-[var(--auth-muted)]">
                {s.record_count} kayıt · Güven:{" "}
                {s.trust_score != null ? `%${s.trust_score}` : "—"}
              </p>
              {s.detail && (
                <p className="mt-1 text-xs text-amber-800">{s.detail}</p>
              )}
              <div className="mt-3">
                <Link
                  href={
                    s.key === "lab"
                      ? `/farms/${farmId}/lab/new`
                      : `/farms/${farmId}/${act.href}`
                  }
                  className="btn btn-secondary w-full text-xs"
                >
                  {s.key === "lab" ? "Rapor yükle" : act.label}
                </Link>
              </div>
            </div>
          );
        })}
      </div>

      {/* Desktop table */}
      <div className="app-surface hidden overflow-x-auto lg:block">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead>
            <tr className="border-b border-[var(--auth-border)] text-[var(--auth-muted)]">
              <th className="px-4 py-3">Kaynak</th>
              <th className="px-4 py-3">Tip</th>
              <th className="px-4 py-3">Durum</th>
              <th className="px-4 py-3">Son güncelleme</th>
              <th className="px-4 py-3">Güven</th>
              <th className="px-4 py-3">Kayıt</th>
              <th className="px-4 py-3">İşlem</th>
            </tr>
          </thead>
          <tbody>
            {sources.map((s) => {
              const act = actions[s.key] || actions.manual;
              return (
                <tr key={s.key} className="border-b border-[var(--auth-border)]">
                  <td className="px-4 py-3">
                    <p className="font-semibold">{s.name}</p>
                    {s.detail && (
                      <p className="text-[10px] text-amber-700">{s.detail}</p>
                    )}
                  </td>
                  <td className="px-4 py-3">{s.source_type}</td>
                  <td className="px-4 py-3">{s.status}</td>
                  <td className="px-4 py-3 text-[var(--auth-muted)]">
                    {s.last_update
                      ? new Date(s.last_update).toLocaleString("tr-TR")
                      : "—"}
                  </td>
                  <td className="px-4 py-3">
                    {s.trust_score != null ? (
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-100">
                          <div
                            className="h-full bg-[var(--auth-forest)]"
                            style={{ width: `${Math.min(100, s.trust_score)}%` }}
                          />
                        </div>
                        <span>%{s.trust_score}</span>
                      </div>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td className="px-4 py-3">{s.record_count}</td>
                  <td className="px-4 py-3">
                    <Link
                      href={
                        s.key === "lab"
                          ? `/farms/${farmId}/lab/new`
                          : `/farms/${farmId}/${act.href}`
                      }
                      className="text-[var(--auth-forest)] hover:underline"
                    >
                      {s.key === "lab" ? "Rapor yükle" : act.label}
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
