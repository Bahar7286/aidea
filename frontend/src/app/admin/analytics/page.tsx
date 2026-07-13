"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "@/components/admin/AdminShell";
import { KpiCard } from "@/components/app/KpiCard";
import { api, AdminAnalytics } from "@/lib/api";

export default function AdminAnalyticsPage() {
  const [days, setDays] = useState(30);
  const [data, setData] = useState<AdminAnalytics | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .adminAnalytics(days)
      .then(setData)
      .catch((err) => setError(err.message));
  }, [days]);

  const series = data?.moisture_series || [];
  const w = 480;
  const h = 160;

  return (
    <AdminShell title="Sistem Raporları ve Analitik">
      {error && <p className="mb-3 text-sm text-red-700">{error}</p>}
      <div className="mb-4 flex gap-2">
        {[7, 30, 90].map((d) => (
          <button
            key={d}
            type="button"
            onClick={() => setDays(d)}
            className={`rounded-full px-3 py-1.5 text-xs font-semibold ${
              days === d
                ? "bg-[var(--auth-forest)] text-white"
                : "bg-white ring-1 ring-[var(--auth-border)]"
            }`}
          >
            {d}g
          </button>
        ))}
      </div>

      <div className="mb-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        <KpiCard
          label="Ort. nem"
          value={
            data?.avg_moisture != null ? `%${data.avg_moisture}` : "—"
          }
        />
        <KpiCard
          label="Ort. sıcaklık"
          value={
            data?.avg_temperature != null
              ? `${data.avg_temperature}°C`
              : "—"
          }
        />
        <KpiCard
          label="Sulama olayı"
          value={String(data?.irrigation_events ?? "—")}
        />
        <KpiCard label="AI tahmin" value={String(data?.predictions ?? "—")} />
        <KpiCard label="Lab rapor" value={String(data?.lab_reports ?? "—")} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="app-surface p-4">
          <p className="mb-2 text-sm font-semibold">Nem trendi</p>
          {series.length < 2 ? (
            <p className="text-xs text-[var(--auth-muted)]">Yetersiz veri</p>
          ) : (
            <svg viewBox={`0 0 ${w} ${h}`} className="h-40 w-full">
              <polyline
                fill="none"
                stroke="#1b4332"
                strokeWidth="2.5"
                points={series
                  .map((p, i) => {
                    const x = 12 + (i / Math.max(series.length - 1, 1)) * (w - 24);
                    const y = h - 12 - (p.avg / 100) * (h - 24);
                    return `${x},${y}`;
                  })
                  .join(" ")}
              />
            </svg>
          )}
        </div>
        <div className="app-surface p-4">
          <p className="mb-2 text-sm font-semibold">Özellik kullanımı</p>
          <ul className="space-y-2 text-sm">
            {(data?.feature_usage || []).map((f) => (
              <li key={f.feature} className="flex justify-between">
                <span>{f.feature}</span>
                <strong>{f.count}</strong>
              </li>
            ))}
          </ul>
          <p className="mt-3 text-[11px] text-[var(--auth-muted)]">
            {data?.note}
          </p>
        </div>
      </div>
    </AdminShell>
  );
}
