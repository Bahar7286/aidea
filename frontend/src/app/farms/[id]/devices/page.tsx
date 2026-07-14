"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/app/AppShell";
import { FarmSelector, setSelectedFarmId } from "@/components/app/FarmSelector";
import { KpiCard } from "@/components/app/KpiCard";
import {
  api,
  Device,
  DeviceSummary,
  Farm,
} from "@/lib/api";

const TYPE_LABELS: Record<string, string> = {
  soil_moisture: "Toprak nemi",
  weather: "Hava istasyonu",
  ec: "EC sensörü",
  flow: "Debi sensörü",
  field_node: "Field Node",
  other: "Diğer",
};

function statusLabel(status: string) {
  const s = status.toLowerCase();
  if (s === "active" || s === "online") return "Çevrimiçi";
  if (s === "warning") return "Uyarı";
  if (s === "offline") return "Çevrimdışı";
  return status;
}

function statusTone(status: string) {
  const s = status.toLowerCase();
  if (s === "active" || s === "online")
    return "bg-emerald-100 text-emerald-800";
  if (s === "warning") return "bg-amber-100 text-amber-900";
  return "bg-slate-200 text-slate-700";
}

export default function DevicesListPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [summary, setSummary] = useState<DeviceSummary | null>(null);
  const [filter, setFilter] = useState<"all" | "active" | "warning" | "offline">(
    "all",
  );
  const [q, setQ] = useState("");
  const [error, setError] = useState("");
  const [okMsg, setOkMsg] = useState("");
  const [measuringId, setMeasuringId] = useState<number | null>(null);

  async function load() {
    const [f, list, sum] = await Promise.all([
      api.getFarm(farmId),
      api.listDevices(farmId, {
        status: filter === "all" ? undefined : filter,
        q: q.trim() || undefined,
      }),
      api.deviceSummary(farmId),
    ]);
    setFarm(f);
    setDevices(list);
    setSummary(sum);
  }

  async function takeReading(deviceId: number) {
    setMeasuringId(deviceId);
    setError("");
    setOkMsg("");
    try {
      const reading = await api.iotSimulateForDevice(
        farmId,
        deviceId,
        "drought_risk",
      );
      await load();
      setOkMsg(
        `Ölçüm alındı (#${deviceId}) · nem %${reading.soil_moisture} · simulation`,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ölçüm alınamadı");
    } finally {
      setMeasuringId(null);
    }
  }

  useEffect(() => {
    if (!farmId) return;
    setSelectedFarmId(farmId);
    load().catch((err) => setError(err.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [farmId, filter]);

  const regionRows = useMemo(() => {
    const map = new Map<string, number>();
    for (const d of devices) {
      const key = d.region_name || "Tanımsız";
      map.set(key, (map.get(key) || 0) + 1);
    }
    return Array.from(map.entries());
  }, [devices]);

  return (
    <AppShell title="Sensör ve Cihazlar" farmName={farm?.name}>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <FarmSelector farmId={farmId} suffixPath="/devices" />
        <span className="rounded-full bg-sky-100 px-2 py-0.5 text-[10px] font-bold text-sky-900">
          Kaynak: simülasyon
        </span>
        <Link
          href={`/farms/${farmId}/sensors/live`}
          className="btn btn-ghost text-sm"
        >
          Canlı veriler
        </Link>
      </div>

      {error && (
        <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>
      )}
      {okMsg && (
        <p className="mb-3 rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
          {okMsg}
        </p>
      )}

      <div className="mb-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard label="Toplam cihaz" value={String(summary?.total ?? "—")} />
        <KpiCard
          label="Çevrimiçi"
          value={
            summary
              ? `${summary.online} (%${summary.online_percent})`
              : "—"
          }
          tone="ok"
        />
        <KpiCard
          label="Uyarı"
          value={String(summary?.warning ?? "—")}
          tone={summary && summary.warning > 0 ? "warn" : undefined}
        />
        <KpiCard
          label="Kalibrasyon bekleyen"
          value={String(summary?.calibration_pending ?? "—")}
          tone={
            summary && summary.calibration_pending > 0 ? "warn" : undefined
          }
        />
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-2">
        {(
          [
            ["all", `Tümü ${summary?.total ?? 0}`],
            ["active", `Aktif ${summary?.online ?? 0}`],
            ["warning", `Uyarı ${summary?.warning ?? 0}`],
            ["offline", `Çevrimdışı ${summary?.offline ?? 0}`],
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
        <form
          className="ml-auto flex w-full gap-2 sm:w-auto"
          onSubmit={(e) => {
            e.preventDefault();
            load().catch((err) => setError(err.message));
          }}
        >
          <input
            className="input text-sm"
            placeholder="Ara (ad / seri no)"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <button type="submit" className="btn btn-secondary text-sm">
            Filtre
          </button>
        </form>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
        <div className="space-y-3">
          {/* Mobile cards */}
          <ul className="space-y-3 lg:hidden">
            {devices.map((d) => (
              <li key={d.id} className="app-surface p-4">
                <Link
                  href={`/farms/${farmId}/devices/${d.id}`}
                  className="block"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-semibold">{d.device_name}</p>
                      <p className="text-xs text-[var(--auth-muted)]">
                        {TYPE_LABELS[d.device_type] || d.device_type}
                        {d.region_name ? ` · ${d.region_name}` : ""}
                      </p>
                    </div>
                    <span
                      className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${statusTone(d.connection_status)}`}
                    >
                      {statusLabel(d.connection_status)}
                    </span>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-3 text-xs text-[var(--auth-muted)]">
                    <span>
                      Nem:{" "}
                      <strong className="text-[var(--auth-ink)]">
                        {d.last_moisture != null ? `%${d.last_moisture}` : "—"}
                      </strong>
                    </span>
                    <span>Pil: {d.battery_percent ?? "—"}%</span>
                    <span>Sinyal: {d.signal_dbm ?? "—"} dBm</span>
                  </div>
                </Link>
                <button
                  type="button"
                  className="btn btn-secondary mt-3 w-full text-xs"
                  disabled={measuringId === d.id}
                  onClick={() => takeReading(d.id)}
                >
                  {measuringId === d.id ? "Ölçülüyor…" : "Ölçüm al"}
                </button>
              </li>
            ))}
            {devices.length === 0 && (
              <li className="rounded-2xl border border-dashed border-[var(--auth-border)] p-8 text-center text-sm text-[var(--auth-muted)]">
                Henüz cihaz yok. Yeni cihaz ekleyin.
              </li>
            )}
          </ul>

          {/* Desktop table */}
          <div className="app-surface hidden overflow-x-auto lg:block">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="border-b border-[var(--auth-border)] text-xs text-[var(--auth-muted)]">
                <tr>
                  <th className="px-4 py-3 font-medium">Cihaz</th>
                  <th className="px-4 py-3 font-medium">Tür</th>
                  <th className="px-4 py-3 font-medium">Bölge</th>
                  <th className="px-4 py-3 font-medium">Son veri</th>
                  <th className="px-4 py-3 font-medium">Pil</th>
                  <th className="px-4 py-3 font-medium">Durum</th>
                  <th className="px-4 py-3 font-medium" />
                </tr>
              </thead>
              <tbody>
                {devices.map((d) => (
                  <tr
                    key={d.id}
                    className="border-b border-[var(--auth-border)] last:border-0"
                  >
                    <td className="px-4 py-3">
                      <p className="font-medium">{d.device_name}</p>
                      <p className="text-xs text-[var(--auth-muted)]">
                        {d.serial_number || "—"}
                      </p>
                    </td>
                    <td className="px-4 py-3">
                      {TYPE_LABELS[d.device_type] || d.device_type}
                    </td>
                    <td className="px-4 py-3">{d.region_name || "—"}</td>
                    <td className="px-4 py-3">
                      {d.last_moisture != null ? `%${d.last_moisture}` : "—"}
                      <span className="block text-[10px] text-[var(--auth-muted)]">
                        {d.last_data_time
                          ? new Date(d.last_data_time).toLocaleString("tr-TR")
                          : "veri yok"}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {d.battery_percent != null ? `${d.battery_percent}%` : "—"}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${statusTone(d.connection_status)}`}
                      >
                        {statusLabel(d.connection_status)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          className="text-xs font-semibold text-[var(--auth-forest)] hover:underline"
                          disabled={measuringId === d.id}
                          onClick={() => takeReading(d.id)}
                        >
                          {measuringId === d.id ? "…" : "Ölçüm al"}
                        </button>
                        <Link
                          href={`/farms/${farmId}/devices/${d.id}`}
                          className="text-[var(--auth-forest)] hover:underline"
                        >
                          Detay
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {devices.length === 0 && (
              <p className="p-8 text-center text-sm text-[var(--auth-muted)]">
                Henüz cihaz yok.
              </p>
            )}
          </div>
        </div>

        <aside className="space-y-4">
          <div className="app-surface p-4">
            <p className="mb-2 text-sm font-semibold">Bölge özeti</p>
            {regionRows.length === 0 ? (
              <p className="text-xs text-[var(--auth-muted)]">Dağılım yok</p>
            ) : (
              <ul className="space-y-2 text-sm">
                {regionRows.map(([name, count]) => (
                  <li key={name} className="flex justify-between gap-2">
                    <span>{name}</span>
                    <strong>{count}</strong>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className="app-surface p-4 text-xs text-[var(--auth-muted)]">
            MVP’de tüm cihaz verileri <strong>simülasyon</strong> kaynaklıdır;
            gerçek sensör gibi gösterilmez.
          </div>
          <Link
            href={`/farms/${farmId}/devices/new`}
            className="btn btn-primary hidden w-full lg:inline-flex"
          >
            + Yeni cihaz ekle
          </Link>
        </aside>
      </div>

      <Link
        href={`/farms/${farmId}/devices/new`}
        className="fixed bottom-20 right-4 z-30 flex items-center gap-2 rounded-full bg-[var(--auth-forest)] px-4 py-3 text-sm font-semibold text-white shadow-lg lg:hidden"
      >
        <span className="text-lg leading-none">+</span> Cihaz
      </Link>
    </AppShell>
  );
}
