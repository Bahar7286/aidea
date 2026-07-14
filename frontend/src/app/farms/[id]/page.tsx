"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/app/AppShell";
import { CropHistoryPanel } from "@/components/app/CropHistoryPanel";
import { setSelectedFarmId } from "@/components/app/FarmSelector";
import {
  AnomalyReport,
  api,
  Farm,
  IrrigationEvent,
  IrrigationStartResult,
  LabReport,
  ManagementZone,
  Prediction,
  ScenarioCompare,
  SensorReading,
} from "@/lib/api";

const riskColor: Record<string, string> = {
  low: "var(--risk-low)",
  medium: "var(--risk-medium)",
  high: "var(--risk-high)",
  critical: "var(--risk-critical)",
};

const riskLabel: Record<string, string> = {
  low: "Düşük",
  medium: "Orta",
  high: "Yüksek",
  critical: "Kritik",
};

const sourceLabel: Record<string, string> = {
  manual: "manuel",
  simulation: "IoT simülasyonu",
  test_dataset: "test veri seti",
  iot: "saha IoT",
  lab_report: "laboratuvar raporu",
  lab_manual: "manuel lab",
};

export default function FarmDetailPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [reading, setReading] = useState<SensorReading | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [scenarios, setScenarios] = useState<ScenarioCompare | null>(null);
  const [anomalies, setAnomalies] = useState<AnomalyReport | null>(null);
  const [history, setHistory] = useState<IrrigationEvent[]>([]);
  const [lastIrrigation, setLastIrrigation] =
    useState<IrrigationStartResult | null>(null);
  const [zones, setZones] = useState<ManagementZone[]>([]);
  const [labReports, setLabReports] = useState<LabReport[]>([]);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const refreshSideData = useCallback(async () => {
    const [anom, hist, zoneRows, labRows] = await Promise.all([
      api.getAnomalies(farmId).catch(() => null),
      api.irrigationHistory(farmId).catch(() => []),
      api.listZones(farmId).catch(() => []),
      api.listLabReports(farmId).catch(() => []),
    ]);
    if (anom) setAnomalies(anom);
    setHistory(hist);
    setZones(zoneRows);
    setLabReports(labRows);
  }, [farmId]);

  useEffect(() => {
    if (!farmId) return;
    setSelectedFarmId(farmId);
    api
      .getFarm(farmId)
      .then(setFarm)
      .catch((err) => setError(err.message));
    api
      .listReadings(farmId)
      .then((rows) => setReading(rows[0] || null))
      .catch(() => undefined);
    api
      .listPredictions(farmId)
      .then((rows) => setPrediction(rows[0] || null))
      .catch(() => undefined);
    refreshSideData();
  }, [farmId, refreshSideData]);

  async function afterDataUpdate(created: SensorReading) {
    setReading(created);
    const pred = await api.predict(farmId);
    setPrediction(pred);
    await refreshSideData();
  }

  async function onSubmitReading(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setLoading(true);
    const form = new FormData(e.currentTarget);
    try {
      const created = await api.createReading(farmId, {
        soil_moisture: Number(form.get("soil_moisture")),
        soil_temperature: Number(form.get("soil_temperature") || 25),
        air_temperature: Number(form.get("air_temperature")),
        air_humidity: Number(form.get("air_humidity") || 42),
        rainfall_probability: Number(form.get("rainfall_probability")),
        last_irrigation_hours_ago: Number(form.get("last_irrigation_hours_ago")),
        source_type: "manual",
      });
      await afterDataUpdate(created);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Veri kaydedilemedi.");
    } finally {
      setLoading(false);
    }
  }

  async function loadDroughtDemo() {
    setLoading(true);
    setError("");
    try {
      const created = await api.iotSimulate(farmId, "drought_risk");
      await afterDataUpdate(created);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Demo yüklenemedi.");
    } finally {
      setLoading(false);
    }
  }

  async function runScenarios() {
    setActionLoading(true);
    setError("");
    try {
      const result = await api.compareScenarios(farmId, [
        "irrigate_now",
        "wait_12h",
        "wait_24h",
        "skip",
      ]);
      setScenarios(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Senaryo çalıştırılamadı.");
    } finally {
      setActionLoading(false);
    }
  }

  async function confirmIrrigation() {
    setActionLoading(true);
    setError("");
    setShowConfirm(false);
    try {
      const duration = prediction?.irrigation_duration ?? 14;
      const result = await api.startIrrigation(farmId, duration);
      setLastIrrigation(result);
      setPrediction(result.prediction);
      const readings = await api.listReadings(farmId);
      setReading(readings[0] || null);
      await refreshSideData();
      const compared = await api.compareScenarios(farmId, [
        "irrigate_now",
        "wait_24h",
      ]);
      setScenarios(compared);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sulama başlatılamadı.");
    } finally {
      setActionLoading(false);
    }
  }

  async function onCreateZone(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    const form = new FormData(e.currentTarget);
    const name = String(form.get("zone_name") || "").trim();
    if (!name) return;
    try {
      await api.createZone({ farm_id: farmId, name });
      e.currentTarget.reset();
      await refreshSideData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Bölge eklenemedi.");
    }
  }

  if (!farm) {
    return (
      <AppShell title="Arazi Detayı">
        <p className="text-muted">{error || "Arazi yükleniyor..."}</p>
      </AppShell>
    );
  }

  const canIrrigate =
    !!prediction &&
    prediction.irrigation_needed &&
    prediction.confidence_score >= 60;

  return (
    <AppShell title="Arazi Detayı" farmName={farm.name}>
    <div className="space-y-6">
      <div className="app-surface flex flex-wrap items-start justify-between gap-3 p-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-2xl font-bold">{farm.name}</h1>
            <span
              className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                farm.is_active !== false
                  ? "bg-emerald-100 text-emerald-800"
                  : "bg-slate-100 text-slate-600"
              }`}
            >
              {farm.is_active !== false ? "Aktif" : "Pasif"}
            </span>
          </div>
          <p className="text-sm text-muted">
            {farm.location || "Konum belirtilmedi"} · {farm.soil_type || "—"} toprak ·{" "}
            {farm.crops[0]?.crop_type || "ürün yok"} · {farm.area ?? "—"} da
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link href={`/farms/${farmId}/twin`} className="btn btn-secondary text-sm">
            Dijital ikiz
          </Link>
          <Link href={`/farms/${farmId}/ai`} className="btn btn-secondary text-sm">
            AI önerileri
          </Link>
          <Link href={`/farms/${farmId}/irrigation`} className="btn btn-secondary text-sm">
            Sulama
          </Link>
          <Link href={`/farms/${farmId}/lab`} className="btn btn-secondary text-sm">
            Laboratuvar
          </Link>
          <Link href={`/farms/${farmId}/devices`} className="btn btn-secondary text-sm">
            Cihazlar
          </Link>
          <Link href={`/farms/${farmId}/sensors/live`} className="btn btn-secondary text-sm">
            Sensörler
          </Link>
          <Link href={`/farms/${farmId}/data/sources`} className="btn btn-secondary text-sm">
            Veri kaynakları
          </Link>
          <Link href={`/farms/${farmId}/edit`} className="btn btn-secondary text-sm">
            Düzenle
          </Link>
          <Link href={`/farms/${farmId}/zones`} className="btn btn-ghost text-sm">
            Bölgeler
          </Link>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.15fr_1fr]">
        <div className="space-y-4">
          <div className="card space-y-3 border-emerald-200 bg-gradient-to-br from-emerald-50/80 to-white">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <h2 className="font-semibold">Canlı sensör (simüle IoT)</h2>
                <p className="text-xs text-muted">
                  Öncelikli veri yolu · <strong>source_type: simulation</strong> · gerçek
                  saha IoT iddiası yok
                </p>
              </div>
              <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
                Simüle IoT
              </span>
            </div>
            {reading && reading.source_type !== "manual" ? (
              <div className="rounded-xl bg-white/80 p-3 text-sm ring-1 ring-emerald-100">
                <p>
                  Nem: <strong>%{reading.soil_moisture}</strong>
                  {reading.soil_moisture_deep != null && (
                    <> · Derin: <strong>%{reading.soil_moisture_deep}</strong></>
                  )}
                </p>
                <p className="text-muted">
                  Sıcaklık {reading.air_temperature ?? "—"}°C · Yağış %
                  {reading.rainfall_probability ?? "—"} · Güven %
                  {reading.data_confidence ?? "—"}
                </p>
              </div>
            ) : (
              <p className="text-sm text-muted">
                Henüz simüle sensör okuması yok. Kuruma senaryosu veya canlı sayfadan
                yükleyin.
              </p>
            )}
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                className="btn btn-primary"
                onClick={loadDroughtDemo}
                disabled={loading}
              >
                {loading ? "Yükleniyor..." : "IoT simülasyon yükle (kuruma)"}
              </button>
              <Link
                href={`/farms/${farmId}/sensors/live`}
                className="btn btn-secondary"
              >
                Canlı sensör paneli
              </Link>
              <Link href={`/farms/${farmId}/twin`} className="btn btn-ghost">
                Dijital ikiz
              </Link>
            </div>
          </div>

          <details className="card group space-y-3" open={!reading}>
            <summary className="cursor-pointer list-none font-semibold marker:content-none">
              <span className="flex items-center justify-between gap-2">
                Manuel override / düzenle
                <span className="text-xs font-normal text-muted group-open:hidden">
                  Açmak için tıklayın
                </span>
              </span>
            </summary>
            <p className="text-xs text-muted">
              Simüle ölçümleri geçersiz kılmak için manuel giriş ·{" "}
              <strong>source_type: manual</strong>
            </p>
            <form className="space-y-3" onSubmit={onSubmitReading}>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                <div>
                  <label className="label" htmlFor="soil_moisture">
                    Toprak nemi (%) *
                  </label>
                  <input
                    className="input"
                    id="soil_moisture"
                    name="soil_moisture"
                    type="number"
                    min={0}
                    max={100}
                    step="0.1"
                    defaultValue={reading?.soil_moisture ?? 34}
                    required
                  />
                </div>
                <div>
                  <label className="label" htmlFor="air_temperature">
                    Hava sıcaklığı (°C) *
                  </label>
                  <input
                    className="input"
                    id="air_temperature"
                    name="air_temperature"
                    type="number"
                    step="0.1"
                    defaultValue={reading?.air_temperature ?? 33}
                    required
                  />
                </div>
                <div>
                  <label className="label" htmlFor="rainfall_probability">
                    Yağış ihtimali (%) *
                  </label>
                  <input
                    className="input"
                    id="rainfall_probability"
                    name="rainfall_probability"
                    type="number"
                    min={0}
                    max={100}
                    defaultValue={reading?.rainfall_probability ?? 5}
                    required
                  />
                </div>
                <div>
                  <label className="label" htmlFor="last_irrigation_hours_ago">
                    Son sulama (saat önce) *
                  </label>
                  <input
                    className="input"
                    id="last_irrigation_hours_ago"
                    name="last_irrigation_hours_ago"
                    type="number"
                    min={0}
                    defaultValue={reading?.last_irrigation_hours_ago ?? 36}
                    required
                  />
                </div>
                <div>
                  <label className="label" htmlFor="soil_temperature">
                    Toprak sıcaklığı (°C)
                  </label>
                  <input
                    className="input"
                    id="soil_temperature"
                    name="soil_temperature"
                    type="number"
                    step="0.1"
                    defaultValue={reading?.soil_temperature ?? 25}
                  />
                </div>
                <div>
                  <label className="label" htmlFor="air_humidity">
                    Hava nemi (%)
                  </label>
                  <input
                    className="input"
                    id="air_humidity"
                    name="air_humidity"
                    type="number"
                    min={0}
                    max={100}
                    defaultValue={reading?.air_humidity ?? 42}
                  />
                </div>
              </div>
              {error && <p className="text-sm text-[var(--risk-critical)]">{error}</p>}
              <button className="btn btn-secondary" disabled={loading}>
                {loading ? "Analiz..." : "Override kaydet ve analiz et"}
              </button>
            </form>
          </details>
        </div>

        <div className="space-y-4">
          <div className="card space-y-2">
            <h2 className="font-semibold">Durum nasıl?</h2>
            {reading ? (
              <>
                <p>
                  Nem (yüzey): <strong>%{reading.soil_moisture}</strong>
                  {reading.soil_moisture_deep != null && (
                    <>
                      {" "}
                      · Derin: <strong>%{reading.soil_moisture_deep}</strong>
                    </>
                  )}
                </p>
                <p>
                  Sıcaklık: {reading.air_temperature ?? "—"}°C · Yağış: %
                  {reading.rainfall_probability ?? "—"}
                </p>
                <p className="text-xs text-muted">
                  Kaynak: {sourceLabel[reading.source_type] || reading.source_type} ·
                  Güven: %{reading.data_confidence ?? "—"}
                  {reading.is_validated === false ? " · doğrulanmadı" : ""}
                </p>
              </>
            ) : (
              <p className="text-sm text-muted">Henüz veri yok.</p>
            )}
          </div>

          <div className="card space-y-2">
            <h2 className="font-semibold">Ne yapmalıyım? / Neden?</h2>
            {prediction ? (
              <>
                <p
                  className="text-lg font-bold"
                  style={{ color: riskColor[prediction.risk_level] }}
                >
                  {prediction.irrigation_needed
                    ? `Sulama öneriliyor${
                        prediction.irrigation_duration
                          ? ` (~${prediction.irrigation_duration} dk)`
                          : ""
                      }`
                    : "Sulama gerekli değil"}
                </p>
                <p>
                  Risk:{" "}
                  <strong style={{ color: riskColor[prediction.risk_level] }}>
                    {riskLabel[prediction.risk_level]}
                  </strong>{" "}
                  · Güven: %{prediction.confidence_score}
                </p>
                <p className="text-sm">{prediction.explanation}</p>
                <p className="text-xs text-muted">
                  Tahmini nem — 24s: %{prediction.moisture_24h} · 48s: %
                  {prediction.moisture_48h} · 72s: %{prediction.moisture_72h}
                </p>
                <div className="flex flex-wrap gap-2 pt-1">
                  <Link
                    href={`/farms/${farmId}/ai`}
                    className="btn btn-secondary text-sm"
                  >
                    AI detay
                  </Link>
                  <Link
                    href={`/farms/${farmId}/irrigation`}
                    className="btn btn-ghost text-sm"
                  >
                    Sulama sayfası
                  </Link>
                </div>
              </>
            ) : (
              <p className="text-sm text-muted">
                IoT simülasyonu yükleyince öneri burada görünür.
              </p>
            )}
          </div>

          {anomalies && anomalies.has_anomalies && (
            <div className="card space-y-2 border-[var(--risk-high)]">
              <h2 className="font-semibold text-[var(--risk-high)]">
                Anomali uyarıları ({anomalies.count})
              </h2>
              <ul className="space-y-2">
                {anomalies.anomalies.map((a) => (
                  <li key={a.code} className="text-sm">
                    <strong style={{ color: riskColor[a.severity] || riskColor.high }}>
                      {a.title}
                    </strong>
                    <span className="text-muted"> — {a.message}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      <section className="grid gap-6 lg:grid-cols-2">
        <form className="card space-y-3" onSubmit={onCreateZone}>
          <h2 className="font-semibold">Yönetim bölgesi</h2>
          <p className="text-xs text-muted">
            Tek sensör tüm araziyi temsil etmez.{" "}
            <Link href={`/farms/${farmId}/zones`} className="text-primary underline">
              Tam bölge ekranı
            </Link>
          </p>
          <div>
            <label className="label" htmlFor="zone_name">
              Bölge adı
            </label>
            <input
              className="input"
              id="zone_name"
              name="zone_name"
              placeholder="Bölge A"
              required
            />
          </div>
          <button className="btn btn-secondary" type="submit">
            Bölge ekle
          </button>
          {zones.length > 0 && (
            <ul className="text-sm text-muted">
              {zones.map((z) => (
                <li key={z.id}>
                  #{z.id} · {z.name}
                </li>
              ))}
            </ul>
          )}
        </form>

        <div className="card space-y-3">
          <h2 className="font-semibold">Toprak analizi (laboratuvar)</h2>
          <p className="text-xs text-muted">
            Lab IoT&apos;nin yerine geçmez — tamamlayıcı kimya. Dosya yükleyin; değerler
            kullanıcı onayı olmadan doğrulanmış sayılmaz. OCR otomatik kayıt yok.
          </p>
          <div className="flex flex-wrap gap-2">
            <Link
              href={`/farms/${farmId}/lab/new`}
              className="btn btn-primary text-sm"
            >
              Rapor dosyası yükle
            </Link>
            <Link href={`/farms/${farmId}/lab`} className="btn btn-secondary text-sm">
              Analiz listesi
            </Link>
          </div>
          {labReports.length > 0 && (
            <ul className="space-y-2 text-sm">
              {labReports.slice(0, 3).map((r) => (
                <li key={r.id} className="border-b border-border pb-2">
                  <Link
                    href={
                      r.user_confirmed
                        ? `/farms/${farmId}/lab/${r.id}`
                        : `/farms/${farmId}/lab/${r.id}/verify`
                    }
                    className="font-semibold text-[var(--auth-forest)] hover:underline"
                  >
                    {r.lab_name}
                  </Link>{" "}
                  · {r.source_type}
                  {r.user_confirmed ? " · onaylı" : " · onay bekliyor"}
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      <section className="card space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="font-semibold">Senaryo karşılaştırması</h2>
            <p className="text-sm text-muted">
              Şimdi sulama, bekleme ve sulama yapmama seçeneklerini karşılaştırın.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={runScenarios}
              disabled={actionLoading || !reading}
            >
              {actionLoading ? "Hesaplanıyor..." : "Senaryoları çalıştır"}
            </button>
            <Link
              href={`/farms/${farmId}/scenarios`}
              className="btn btn-ghost text-sm"
            >
              Tam senaryo sayfası
            </Link>
          </div>
        </div>
        {scenarios ? (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead>
                <tr className="border-b border-border text-muted">
                  <th className="py-2 pr-3">Senaryo</th>
                  <th className="py-2 pr-3">Tahmini nem</th>
                  <th className="py-2 pr-3">Su (L)</th>
                  <th className="py-2 pr-3">Risk</th>
                  <th className="py-2 pr-3">Bitki stresi</th>
                  <th className="py-2">Sonuç</th>
                </tr>
              </thead>
              <tbody>
                {scenarios.results.map((row) => (
                  <tr
                    key={row.scenario}
                    className={`border-b border-border ${
                      row.recommended ? "bg-green-50" : ""
                    }`}
                  >
                    <td className="py-2 pr-3 font-medium">
                      {row.label}
                      {row.recommended && (
                        <span className="ml-2 text-xs text-primary">önerilen</span>
                      )}
                    </td>
                    <td className="py-2 pr-3">%{row.estimated_moisture}</td>
                    <td className="py-2 pr-3">
                      {row.estimated_water_liters ?? "—"}
                    </td>
                    <td
                      className="py-2 pr-3 font-medium"
                      style={{ color: riskColor[row.risk_level] }}
                    >
                      {riskLabel[row.risk_level]}
                    </td>
                    <td className="py-2 pr-3">{row.plant_stress}</td>
                    <td className="py-2 text-muted">{row.explanation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="mt-2 text-xs text-muted">
              Mevcut nem: %{scenarios.current_moisture}
            </p>
          </div>
        ) : (
          <p className="text-sm text-muted">
            Karşılaştırma için önce veri girin, sonra senaryoları çalıştırın.
          </p>
        )}
      </section>

      <CropHistoryPanel farmId={farmId} />

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="card space-y-3">
          <h2 className="font-semibold">Sanal sulama otomasyonu</h2>
          <p className="text-sm text-muted">
            Kullanıcı onayı olmadan sulama başlamaz. Güven skoru %60 altında
            otomasyon önerilmez.
          </p>
          <div className="rounded-lg border border-border bg-[var(--background)] p-3 text-sm">
            <p>
              Vana durumu:{" "}
              <strong>
                {lastIrrigation?.event.valve_status ||
                  history[0]?.valve_status ||
                  "kapalı"}
              </strong>
            </p>
            {lastIrrigation && (
              <p className="mt-1 text-muted">{lastIrrigation.message}</p>
            )}
          </div>
          {!canIrrigate && prediction && (
            <p className="text-xs text-muted">
              {prediction.confidence_score < 60
                ? "Güven skoru düşük — otomasyon kapalı."
                : "Şu an sulama önerilmiyor."}
            </p>
          )}
          <button
            type="button"
            className="btn btn-primary"
            disabled={!canIrrigate || actionLoading}
            onClick={() => setShowConfirm(true)}
          >
            Sulamayı başlat
          </button>
        </div>

        <div className="card space-y-3">
          <h2 className="font-semibold">Sulama geçmişi</h2>
          {history.length === 0 ? (
            <p className="text-sm text-muted">Henüz sulama kaydı yok.</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {history.slice(0, 5).map((ev) => (
                <li
                  key={ev.id}
                  className="flex flex-wrap justify-between gap-2 border-b border-border pb-2"
                >
                  <span>
                    #{ev.id} · {ev.status} · vana {ev.valve_status}
                  </span>
                  <span className="text-muted">
                    {ev.duration ?? "—"} dk · {ev.water_amount ?? "—"} L
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      {showConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="card max-w-md space-y-4 shadow-lg">
            <h3 className="text-lg font-semibold">Sulamayı onayla</h3>
            <p className="text-sm text-muted">
              Sanal vana açılacak, yaklaşık{" "}
              <strong>{prediction?.irrigation_duration ?? 14} dakika</strong> sulama
              simüle edilecek ve nem değeri güncellenecek. Devam etmek istiyor
              musunuz?
            </p>
            <div className="flex justify-end gap-2">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowConfirm(false)}
              >
                Vazgeç
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={confirmIrrigation}
                disabled={actionLoading}
              >
                Onayla ve başlat
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
    </AppShell>
  );
}
