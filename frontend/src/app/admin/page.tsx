"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "@/components/admin/AdminShell";
import { KpiCard } from "@/components/app/KpiCard";
import { api, AdminOverview } from "@/lib/api";

export default function AdminOverviewPage() {
  const [data, setData] = useState<AdminOverview | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .adminOverview()
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <AdminShell title="Yönetim Paneli">
      {error && <p className="mb-3 text-sm text-red-700">{error}</p>}
      <div className="mb-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        <KpiCard label="Kullanıcı" value={String(data?.total_users ?? "—")} />
        <KpiCard label="Çiftlik" value={String(data?.total_farms ?? "—")} />
        <KpiCard
          label="Aktif cihaz"
          value={String(data?.online_devices ?? "—")}
          tone="ok"
        />
        <KpiCard
          label="Ort. nem"
          value={
            data?.avg_soil_moisture != null
              ? `%${data.avg_soil_moisture}`
              : "—"
          }
        />
        <KpiCard
          label="Sistem sağlığı"
          value={data ? `%${data.system_health_pct}` : "—"}
          tone="ok"
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="app-surface p-4">
          <p className="mb-2 text-sm font-semibold">Son uyarılar</p>
          <ul className="space-y-2 text-sm">
            {(data?.recent_alerts || []).map((a, i) => (
              <li key={`${a.title}-${i}`} className="border-b border-[var(--auth-border)] pb-2 last:border-0">
                <span className="font-medium">{a.title}</span>
                <span className="ml-2 text-[10px] uppercase text-[var(--auth-muted)]">
                  {a.severity}
                </span>
                <p className="text-xs text-[var(--auth-muted)]">{a.message}</p>
              </li>
            ))}
            {data && data.recent_alerts.length === 0 && (
              <li className="text-xs text-[var(--auth-muted)]">Uyarı yok</li>
            )}
          </ul>
        </div>
        <div className="app-surface p-4">
          <p className="mb-2 text-sm font-semibold">Son aktiviteler</p>
          <ul className="space-y-2 text-xs text-[var(--auth-muted)]">
            {(data?.recent_activity || []).map((line) => (
              <li key={line}>· {line}</li>
            ))}
          </ul>
          <p className="mt-3 text-[11px] text-[var(--auth-muted)]">{data?.note}</p>
        </div>
      </div>
    </AdminShell>
  );
}
