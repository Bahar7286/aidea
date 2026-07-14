"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/app/AppShell";
import {
  getSelectedFarmId,
  setSelectedFarmId,
} from "@/components/app/FarmSelector";
import { KpiCard } from "@/components/app/KpiCard";
import { FarmMapPanel } from "@/components/app/FarmMapPanel";
import { MoistureSparkline } from "@/components/app/MoistureSparkline";
import { api, Farm, FarmOverview, WeatherSnapshot } from "@/lib/api";

const riskLabel: Record<string, string> = {
  low: "Düşük",
  medium: "Orta",
  high: "Yüksek",
  critical: "Kritik",
};

export default function DashboardPage() {
  const [farms, setFarms] = useState<Farm[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [overview, setOverview] = useState<FarmOverview | null>(null);
  const [weather, setWeather] = useState<WeatherSnapshot | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listFarms()
      .then((rows) => {
        setFarms(rows);
        const preferred =
          getSelectedFarmId() ||
          rows.find((f) => f.is_active !== false)?.id ||
          rows[0]?.id;
        if (preferred) {
          setSelectedId(preferred);
          setSelectedFarmId(preferred);
        }
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setOverview(null);
      return;
    }
    setSelectedFarmId(selectedId);
    api
      .farmOverview(selectedId)
      .then(setOverview)
      .catch((err) => setError(err.message));
    api
      .getWeather(selectedId)
      .then(setWeather)
      .catch(() => setWeather(null));
  }, [selectedId]);

  const reading = overview?.latest_reading;
  const prediction = overview?.latest_prediction;
  const moisture = reading?.soil_moisture;
  const risk = prediction?.risk_level || "low";
  const confidence = reading?.data_confidence ?? prediction?.confidence_score;

  const zones = (overview?.zone_names?.length
    ? overview.zone_names
    : ["Kuzey", "Orta", "Güney"]
  ).map((name, i) => ({
    name,
    moisture:
      moisture != null
        ? Math.max(10, Math.min(50, moisture + (i - 1) * 3))
        : null,
  }));

  return (
    <AppShell title="Genel Bakış" farmName={overview?.farm.name}>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <label className="text-sm font-medium text-[var(--auth-muted)]">
          Arazi
        </label>
        <select
          className="input max-w-xs"
          value={selectedId ?? ""}
          onChange={(e) => {
            const id = Number(e.target.value) || null;
            setSelectedId(id);
            if (id) setSelectedFarmId(id);
          }}
        >
          {farms.length === 0 && <option value="">Arazi yok</option>}
          {farms.map((f) => (
            <option key={f.id} value={f.id}>
              {f.name}
            </option>
          ))}
        </select>
        <Link href="/farms/new" className="btn btn-primary text-sm">
          + Yeni arazi
        </Link>
      </div>

      {error && (
        <p className="mb-4 text-sm text-[var(--risk-critical)]">{error}</p>
      )}

      {farms.length === 0 ? (
        <div className="app-surface p-6 text-sm text-[var(--auth-muted)]">
          Henüz arazi yok.{" "}
          <Link href="/farms/new" className="font-semibold text-[var(--auth-forest)]">
            İlk arazinizi ekleyin
          </Link>
          .
        </div>
      ) : (
        <div className="space-y-5">
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard
              label="Toprak nemi"
              value={moisture != null ? `%${moisture}` : "—"}
              hint={
                moisture != null
                  ? moisture >= 25 && moisture <= 35
                    ? "İyi · Hedef 25–35%"
                    : "Hedef aralık dışı"
                  : "Veri girin veya IoT simülasyonu çalıştırın"
              }
              tone={
                moisture == null
                  ? "neutral"
                  : moisture >= 25 && moisture <= 35
                    ? "ok"
                    : "warn"
              }
            />
            <KpiCard
              label="24 saatlik risk"
              value={riskLabel[risk] || risk}
              hint={
                prediction?.irrigation_needed
                  ? "Sulama öneriliyor"
                  : "Şimdilik izlenebilir"
              }
              tone={risk === "low" ? "ok" : "warn"}
            />
            <KpiCard
              label="Su tasarrufu"
              value={
                overview?.water_savings_liters != null
                  ? `${Math.round(overview.water_savings_liters)} L`
                  : "—"
              }
              hint={
                overview?.water_savings_pct != null
                  ? `Tahmini %${overview.water_savings_pct} · kural tabanlı`
                  : overview?.water_usage_note ||
                    "Sulama geçmişi yok — rapor için sanal sulama çalıştırın"
              }
              tone={
                overview?.water_savings_liters != null &&
                overview.water_savings_liters > 0
                  ? "ok"
                  : "neutral"
              }
            />
            <KpiCard
              label="Veri güveni"
              value={confidence != null ? `%${Math.round(confidence)}` : "—"}
              hint={
                reading?.source_type
                  ? `Kaynak: ${reading.source_type}`
                  : "Ölçüm bekleniyor"
              }
              tone={confidence != null && confidence >= 70 ? "ok" : "neutral"}
            />
          </div>

          <div className="grid gap-4 lg:grid-cols-5">
            <div className="lg:col-span-3">
              <FarmMapPanel
                farm={overview?.farm}
                zones={zones}
                areaDa={overview?.farm.area}
                sourceType={reading?.source_type || "simulation"}
                title="Arazi haritası"
                subtitle={
                  overview?.farm.location
                    ? `${overview.farm.location} · OpenStreetMap + nem`
                    : "OpenStreetMap + nem bölgeler"
                }
                heightClass="h-72 sm:h-80 lg:h-[22rem]"
              />
            </div>
            <div className="space-y-4 lg:col-span-2">
              <MoistureSparkline
                points={[
                  moisture,
                  prediction?.moisture_24h,
                  prediction?.moisture_48h,
                  prediction?.moisture_72h,
                ]}
              />
              <div className="app-surface grid gap-3 p-4 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
                <div>
                  <p className="text-xs text-[var(--auth-muted)]">Hava (Open-Meteo)</p>
                  <p className="text-lg font-bold">
                    {weather?.temperature_c != null
                      ? `${weather.temperature_c.toFixed(0)} °C`
                      : "—"}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-[var(--auth-muted)]">Nem</p>
                  <p className="text-lg font-bold">
                    {weather?.humidity_pct != null
                      ? `%${weather.humidity_pct.toFixed(0)}`
                      : "—"}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-[var(--auth-muted)]">Yağış ihtimali</p>
                  <p className="text-lg font-bold">
                    {weather?.precip_probability_pct != null
                      ? `%${weather.precip_probability_pct.toFixed(0)}`
                      : "—"}
                  </p>
                </div>
                {weather?.error && (
                  <p className="sm:col-span-3 text-xs text-amber-800 xl:col-span-3">
                    {weather.error}
                  </p>
                )}
              </div>
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-3">
            <div className="app-surface space-y-2 p-4 lg:col-span-2">
              <h2 className="font-semibold">Durum nasıl? / Ne yapmalıyım?</h2>
              {prediction ? (
                <>
                  <p className="text-lg font-bold text-[var(--auth-forest)]">
                    {prediction.irrigation_needed
                      ? `Sulama öneriliyor${
                          prediction.irrigation_duration
                            ? ` (~${prediction.irrigation_duration} dk)`
                            : ""
                        }`
                      : "Sulama gerekli değil"}
                  </p>
                  <p className="text-sm text-[var(--auth-muted)]">
                    {prediction.explanation}
                  </p>
                  <div className="flex flex-wrap gap-2 pt-2">
                    <Link
                      href={`/farms/${selectedId}/sensors/live`}
                      className="btn btn-primary text-sm"
                    >
                      Canlı sensör
                    </Link>
                    <Link
                      href={`/farms/${selectedId}/irrigation`}
                      className="btn btn-secondary text-sm"
                    >
                      Sulama
                    </Link>
                    <Link
                      href={`/farms/${selectedId}/scenarios`}
                      className="btn btn-ghost text-sm"
                    >
                      Senaryolar
                    </Link>
                    <Link
                      href={`/farms/${selectedId}/ai`}
                      className="btn btn-ghost text-sm"
                    >
                      AI önerileri
                    </Link>
                  </div>
                </>
              ) : (
                <p className="text-sm text-[var(--auth-muted)]">
                  Bu arazi için henüz AI önerisi yok.{" "}
                  <Link
                    href={`/farms/${selectedId}`}
                    className="font-semibold text-[var(--auth-forest)]"
                  >
                    IoT simülasyonu yükleyip analiz edin
                  </Link>
                  .
                </p>
              )}
            </div>

            <div className="app-surface space-y-3 p-4">
              <h2 className="font-semibold">Hızlı durum</h2>
              <p className="text-sm text-[var(--auth-muted)]">
                Bölge: {overview?.zone_names.length || 0} · Cihaz:{" "}
                {overview?.farm.device_count ?? 0}
              </p>
              <p className="text-sm text-[var(--auth-muted)]">
                Anomali: {overview?.anomaly_count ?? 0}
              </p>
              <p className="text-sm text-[var(--auth-muted)]">
                Vana: {overview?.open_irrigation ? "açık (sim)" : "kapalı"}
              </p>
              <Link
                href={`/farms/${selectedId}/zones`}
                className="btn btn-secondary w-full text-sm"
              >
                Bölgeleri yönet
              </Link>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
