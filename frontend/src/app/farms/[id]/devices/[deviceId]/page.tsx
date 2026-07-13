"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app/AppShell";
import { HistoryChart } from "@/components/app/HistoryChart";
import { setSelectedFarmId } from "@/components/app/FarmSelector";
import { api, DeviceDetail, Farm } from "@/lib/api";

function statusLabel(status: string) {
  const s = status.toLowerCase();
  if (s === "active" || s === "online") return "Çevrimiçi";
  if (s === "warning") return "Uyarı";
  if (s === "offline") return "Çevrimdışı";
  return status;
}

export default function DeviceDetailPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const deviceId = Number(params.deviceId);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [detail, setDetail] = useState<DeviceDetail | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    const [f, d] = await Promise.all([
      api.getFarm(farmId),
      api.getDeviceDetail(deviceId),
    ]);
    setFarm(f);
    setDetail(d);
  }

  useEffect(() => {
    if (!farmId || !deviceId) return;
    setSelectedFarmId(farmId);
    load().catch((err) => setError(err.message));
  }, [farmId, deviceId]);

  async function runSim() {
    setBusy(true);
    setError("");
    try {
      await api.iotSimulateForDevice(farmId, deviceId, "drought_risk");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Simülasyon başarısız");
    } finally {
      setBusy(false);
    }
  }

  async function runTest() {
    setBusy(true);
    setError("");
    try {
      await api.testDevice(deviceId);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Test başarısız");
    } finally {
      setBusy(false);
    }
  }

  const d = detail?.device;
  const chartValues = (detail?.recent_readings || [])
    .slice()
    .reverse()
    .map((r) => r.soil_moisture);

  return (
    <AppShell title="Cihaz Detayı" farmName={farm?.name}>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <Link
          href={`/farms/${farmId}/devices`}
          className="text-sm text-[var(--auth-forest)] hover:underline"
        >
          ← Cihazlar
        </Link>
        <span className="rounded-full bg-sky-100 px-2 py-0.5 text-[10px] font-bold text-sky-900">
          {d?.source_label || "simulation"}
        </span>
      </div>

      {error && (
        <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>
      )}

      {!d ? (
        <p className="text-sm text-[var(--auth-muted)]">Yükleniyor…</p>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
          <div className="space-y-4">
            <div className="app-surface flex flex-wrap items-start justify-between gap-3 p-4">
              <div>
                <h1 className="text-xl font-bold">{d.device_name}</h1>
                <p className="text-sm text-[var(--auth-muted)]">
                  {d.serial_number || "Seri no yok"} · {d.device_type} ·{" "}
                  {d.depth_cm ?? 20} cm
                </p>
              </div>
              <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
                {statusLabel(d.connection_status)}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[
                {
                  label: "Son ölçüm",
                  value:
                    d.last_moisture != null ? `%${d.last_moisture}` : "—",
                },
                {
                  label: "Pil",
                  value:
                    d.battery_percent != null ? `${d.battery_percent}%` : "—",
                },
                {
                  label: "Sinyal",
                  value: d.signal_dbm != null ? `${d.signal_dbm} dBm` : "—",
                },
                {
                  label: "Son senkron",
                  value: d.last_data_time
                    ? new Date(d.last_data_time).toLocaleString("tr-TR")
                    : "—",
                },
              ].map((item) => (
                <div key={item.label} className="app-surface p-3">
                  <p className="text-[11px] text-[var(--auth-muted)]">
                    {item.label}
                  </p>
                  <p className="mt-1 text-sm font-semibold">{item.value}</p>
                </div>
              ))}
            </div>

            <HistoryChart
              values={chartValues}
              label="Son ölçümler"
              unit="% hacimsel"
            />

            {d.calibration_due && (
              <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950">
                <p>Kalibrasyon zamanı yaklaşıyor veya henüz yapılmadı.</p>
                <Link
                  href={`/farms/${farmId}/devices/${deviceId}/calibrate`}
                  className="btn btn-secondary text-xs"
                >
                  Kalibrasyona git
                </Link>
              </div>
            )}

            <div className="app-surface overflow-hidden">
              <table className="w-full text-sm">
                <tbody>
                  {[
                    ["Firmware", d.firmware_version || "—"],
                    [
                      "Kurulum",
                      d.installed_at
                        ? new Date(d.installed_at).toLocaleDateString("tr-TR")
                        : "—",
                    ],
                    [
                      "Son kalibrasyon",
                      d.last_calibration_at
                        ? new Date(d.last_calibration_at).toLocaleDateString(
                            "tr-TR",
                          )
                        : "—",
                    ],
                    ["Bağlantı", d.connection_type || "—"],
                    ["Bölge", d.region_name || "—"],
                    [
                      "Ofset",
                      d.calibration_offset != null
                        ? String(d.calibration_offset)
                        : "0",
                    ],
                  ].map(([k, v]) => (
                    <tr
                      key={k}
                      className="border-b border-[var(--auth-border)] last:border-0"
                    >
                      <td className="px-4 py-2.5 text-[var(--auth-muted)]">
                        {k}
                      </td>
                      <td className="px-4 py-2.5 font-medium">{v}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                className="btn btn-secondary text-sm"
                onClick={runSim}
                disabled={busy}
              >
                Simülasyon ölçümü
              </button>
              <button
                type="button"
                className="btn btn-secondary text-sm"
                onClick={runTest}
                disabled={busy}
              >
                Bağlantı testi
              </button>
              <Link
                href={`/farms/${farmId}/devices/${deviceId}/calibrate`}
                className="btn btn-primary text-sm"
              >
                Kurulum / kalibrasyon
              </Link>
            </div>
          </div>

          <aside className="space-y-4">
            <div className="app-surface p-4">
              <p className="mb-2 text-sm font-semibold">Olay geçmişi</p>
              <ul className="space-y-2 text-xs text-[var(--auth-muted)]">
                {(detail?.events || []).map((ev) => (
                  <li
                    key={ev}
                    className="border-l-2 border-[var(--auth-forest)] pl-2"
                  >
                    {ev}
                  </li>
                ))}
              </ul>
            </div>
          </aside>
        </div>
      )}
    </AppShell>
  );
}
