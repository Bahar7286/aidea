"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/app/AppShell";
import { FarmSelector, setSelectedFarmId } from "@/components/app/FarmSelector";
import { KpiCard } from "@/components/app/KpiCard";
import {
  AnomalyReport,
  api,
  Farm,
  SensorReading,
  WeatherSnapshot,
} from "@/lib/api";

export default function LiveSensorsPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [reading, setReading] = useState<SensorReading | null>(null);
  const [prev, setPrev] = useState<SensorReading | null>(null);
  const [anomalies, setAnomalies] = useState<AnomalyReport | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [scenario, setScenario] = useState("drought_risk");
  const [datasets, setDatasets] = useState<
    Array<{ id: string; name: string }>
  >([]);
  const [weather, setWeather] = useState<WeatherSnapshot | null>(null);

  async function load() {
    const [f, readings, anom] = await Promise.all([
      api.getFarm(farmId),
      api.listReadings(farmId, 10),
      api.getAnomalies(farmId).catch(() => null),
    ]);
    setFarm(f);
    setReading(readings[0] || null);
    setPrev(readings[1] || null);
    setAnomalies(anom);
  }

  useEffect(() => {
    if (!farmId) return;
    setSelectedFarmId(farmId);
    load().catch((err) => setError(err.message));
    api
      .listDatasets()
      .then((rows) => {
        const mapped = rows.map((r) => ({ id: r.id, name: r.name }));
        setDatasets(mapped);
        if (mapped.length && !mapped.some((d) => d.id === scenario)) {
          setScenario(mapped[0].id);
        }
      })
      .catch(() => undefined);
    api
      .getWeather(farmId)
      .then(setWeather)
      .catch(() => setWeather(null));
  }, [farmId]);

  async function simulate() {
    setLoading(true);
    setError("");
    try {
      await api.iotSimulate(farmId, scenario);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Simülasyon başarısız");
    } finally {
      setLoading(false);
    }
  }

  async function loadTestDataset() {
    setLoading(true);
    setError("");
    try {
      await api.loadDataset(farmId, scenario);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Test veri yüklenemedi");
    } finally {
      setLoading(false);
    }
  }

  function delta(curr?: number | null, before?: number | null) {
    if (curr == null || before == null) return null;
    return +(curr - before).toFixed(1);
  }

  const dMoist = delta(reading?.soil_moisture, prev?.soil_moisture);
  const online = farm?.device_count ?? 0;

  return (
    <AppShell title="Canlı Sensör Verileri" farmName={farm?.name}>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <FarmSelector farmId={farmId} suffixPath="/sensors/live" />
        <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
          Canlı
        </span>
        <select
          className="input max-w-[14rem] text-sm"
          value={scenario}
          onChange={(e) => setScenario(e.target.value)}
          aria-label="Senaryo"
        >
          {(datasets.length
            ? datasets
            : [{ id: "drought_risk", name: "Kuruma riski" }]
          ).map((d) => (
            <option key={d.id} value={d.id}>
              {d.name}
            </option>
          ))}
        </select>
        <button
          type="button"
          className="btn btn-secondary text-sm"
          onClick={simulate}
          disabled={loading}
        >
          {loading ? "…" : "IoT simülasyon"}
        </button>
        <button
          type="button"
          className="btn btn-ghost text-sm"
          onClick={loadTestDataset}
          disabled={loading}
        >
          Test veri seti
        </button>
        <Link href={`/farms/${farmId}/data/manual`} className="btn btn-ghost text-sm">
          Manuel giriş
        </Link>
      </div>

      {error && <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>}

      <div className="mb-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <KpiCard
          label="Toprak nemi"
          value={reading ? `%${reading.soil_moisture}` : "—"}
          hint={
            dMoist != null
              ? `${dMoist > 0 ? "+" : ""}${dMoist} vs önceki`
              : "Hedef %25–35"
          }
          tone="ok"
        />
        <KpiCard
          label="Toprak sıcaklığı"
          value={
            reading?.soil_temperature != null
              ? `${reading.soil_temperature} °C`
              : "—"
          }
          hint="Önerilen 22–28 °C"
        />
        <KpiCard
          label="Hava sıcaklığı"
          value={
            weather?.temperature_c != null
              ? `${weather.temperature_c.toFixed(0)} °C`
              : reading?.air_temperature != null
                ? `${reading.air_temperature} °C`
                : "—"
          }
          hint={
            weather?.precip_probability_pct != null
              ? `Yağış ihtimali %${weather.precip_probability_pct.toFixed(0)} · Open-Meteo`
              : "Open-Meteo veya okuma"
          }
        />
        <KpiCard
          label="Hava nemi"
          value={
            weather?.humidity_pct != null
              ? `%${weather.humidity_pct.toFixed(0)}`
              : reading?.air_humidity != null
                ? `%${reading.air_humidity}`
                : "—"
          }
        />
        <KpiCard
          label="EC"
          value={reading?.ec != null ? String(reading.ec) : "—"}
          hint="Tuzluluk eğilimi"
        />
        <KpiCard
          label="Veri güveni"
          value={
            reading?.data_confidence != null
              ? `%${Math.round(reading.data_confidence)}`
              : "—"
          }
          hint={
            reading
              ? `Kaynak: ${reading.source_type}${
                  reading.source_type === "simulation" ? " (simülasyon)" : ""
                }`
              : "Ölçüm yok"
          }
          tone={
            reading?.source_type === "simulation" ? "warn" : "neutral"
          }
        />
      </div>

      <div className="mb-4 grid gap-3 sm:grid-cols-3">
        <div className="app-surface p-4 text-sm">
          <p className="text-[var(--auth-muted)]">Cihaz</p>
          <p className="text-xl font-bold">{online}</p>
        </div>
        <div className="app-surface p-4 text-sm">
          <p className="text-[var(--auth-muted)]">Son güncelleme</p>
          <p className="text-sm font-semibold">
            {reading
              ? new Date(reading.timestamp).toLocaleString("tr-TR")
              : "—"}
          </p>
        </div>
        <div className="app-surface p-4 text-sm">
          <p className="text-[var(--auth-muted)]">Doğrulama</p>
          <p className="text-xl font-bold">
            {reading?.is_validated === false ? "Hayır" : "Evet"}
          </p>
        </div>
      </div>

      {anomalies?.has_anomalies && (
        <div className="mb-4 rounded-2xl border border-orange-200 bg-orange-50 p-4">
          <p className="font-semibold text-orange-900">
            Anomali uyarıları ({anomalies.count})
          </p>
          <ul className="mt-2 space-y-1 text-sm text-orange-900/80">
            {anomalies.anomalies.map((a) => (
              <li key={a.code}>
                <strong>{a.title}</strong> — {a.message}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="app-surface overflow-x-auto">
        <table className="w-full min-w-[560px] text-left text-sm">
          <thead>
            <tr className="border-b border-[var(--auth-border)] text-[var(--auth-muted)]">
              <th className="px-4 py-3">Metrik</th>
              <th className="px-4 py-3">Değer</th>
              <th className="px-4 py-3">Durum</th>
              <th className="px-4 py-3">Zaman</th>
            </tr>
          </thead>
          <tbody>
            {[
              ["Toprak nemi (yüzey)", reading?.soil_moisture, "%"],
              ["Toprak nemi (derin)", reading?.soil_moisture_deep, "%"],
              ["Toprak sıcaklığı", reading?.soil_temperature, "°C"],
              ["Hava sıcaklığı", reading?.air_temperature, "°C"],
              ["Hava nemi", reading?.air_humidity, "%"],
              ["EC", reading?.ec, ""],
            ].map(([label, val, unit]) => (
              <tr key={String(label)} className="border-b border-[var(--auth-border)]">
                <td className="px-4 py-3 font-medium">{label}</td>
                <td className="px-4 py-3">
                  {val != null ? `${val}${unit}` : "—"}
                </td>
                <td className="px-4 py-3">
                  <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
                    {val != null ? "Normal" : "Veri yok"}
                  </span>
                </td>
                <td className="px-4 py-3 text-[var(--auth-muted)]">
                  {reading
                    ? new Date(reading.timestamp).toLocaleTimeString("tr-TR")
                    : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
