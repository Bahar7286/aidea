"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/app/AppShell";
import { FarmSelector, setSelectedFarmId } from "@/components/app/FarmSelector";
import { HistoryChart } from "@/components/app/HistoryChart";
import { api, Farm, SensorReading } from "@/lib/api";

type MetricKey =
  | "soil_moisture"
  | "soil_temperature"
  | "air_temperature"
  | "air_humidity"
  | "ec";

const METRICS: Array<{ key: MetricKey; label: string; unit: string }> = [
  { key: "soil_moisture", label: "Toprak nemi", unit: "%" },
  { key: "soil_temperature", label: "Toprak sıcaklığı", unit: "°C" },
  { key: "air_temperature", label: "Hava sıcaklığı", unit: "°C" },
  { key: "air_humidity", label: "Hava nemi", unit: "%" },
  { key: "ec", label: "EC", unit: "" },
];

export default function HistoryPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [metric, setMetric] = useState<MetricKey>("soil_moisture");
  const [period, setPeriod] = useState<"24h" | "72h" | "7d" | "30d" | "all">("72h");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!farmId) return;
    setSelectedFarmId(farmId);
    Promise.all([api.getFarm(farmId), api.listReadings(farmId, 200)])
      .then(([f, rows]) => {
        setFarm(f);
        setReadings(rows);
      })
      .catch((err) => setError(err.message));
  }, [farmId]);

  const filtered = useMemo(() => {
    const now = Date.now();
    const ms =
      period === "24h"
        ? 24 * 3600e3
        : period === "72h"
          ? 72 * 3600e3
          : period === "7d"
            ? 7 * 24 * 3600e3
            : period === "30d"
              ? 30 * 24 * 3600e3
              : Infinity;
    return readings
      .filter((r) => now - new Date(r.timestamp).getTime() <= ms)
      .slice()
      .reverse(); // oldest first for chart
  }, [readings, period]);

  const values = filtered.map((r) => r[metric] as number | null | undefined);
  const labels = filtered.map((r) =>
    new Date(r.timestamp).toLocaleString("tr-TR", {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    }),
  );
  const meta = METRICS.find((m) => m.key === metric)!;

  return (
    <AppShell title="Geçmiş Veri Grafikleri" farmName={farm?.name}>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <FarmSelector farmId={farmId} suffixPath="/sensors/history" />
        <select
          className="input max-w-[180px] text-sm"
          value={metric}
          onChange={(e) => setMetric(e.target.value as MetricKey)}
        >
          {METRICS.map((m) => (
            <option key={m.key} value={m.key}>
              {m.label}
            </option>
          ))}
        </select>
        <div className="flex flex-wrap gap-1">
          {(
            [
              ["24h", "24 Saat"],
              ["72h", "72 Saat"],
              ["7d", "7 Gün"],
              ["30d", "30 Gün"],
              ["all", "Tümü"],
            ] as const
          ).map(([id, label]) => (
            <button
              key={id}
              type="button"
              onClick={() => setPeriod(id)}
              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                period === id
                  ? "bg-[var(--auth-forest)] text-white"
                  : "bg-white ring-1 ring-[var(--auth-border)] text-[var(--auth-muted)]"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <Link href={`/farms/${farmId}/sensors/live`} className="btn btn-ghost text-sm">
          Canlı
        </Link>
      </div>

      {error && <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>}

      <HistoryChart
        values={values}
        labels={labels}
        label={meta.label}
        unit={meta.unit}
      />

      <div className="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50/70 p-4 text-sm">
        <p className="font-semibold text-[var(--auth-forest)]">AI notu</p>
        <p className="mt-1 text-[var(--auth-muted)]">
          {filtered.length === 0
            ? "Bu dönemde ölçüm yok. Manuel giriş veya simülasyon ekleyin."
            : `${filtered.length} ölçüm gösteriliyor. Kaynak etiketleri her kayıtta tutulur; simülasyon gerçek sensör değildir.`}
        </p>
      </div>

      <div className="mt-4 app-surface overflow-x-auto">
        <table className="w-full min-w-[480px] text-left text-sm">
          <thead>
            <tr className="border-b border-[var(--auth-border)] text-[var(--auth-muted)]">
              <th className="px-4 py-2">Zaman</th>
              <th className="px-4 py-2">Değer</th>
              <th className="px-4 py-2">Kaynak</th>
            </tr>
          </thead>
          <tbody>
            {[...filtered].reverse().slice(0, 20).map((r) => (
              <tr key={r.id} className="border-b border-[var(--auth-border)]">
                <td className="px-4 py-2">
                  {new Date(r.timestamp).toLocaleString("tr-TR")}
                </td>
                <td className="px-4 py-2">
                  {r[metric] != null ? `${r[metric]}${meta.unit}` : "—"}
                </td>
                <td className="px-4 py-2 text-[var(--auth-muted)]">{r.source_type}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
