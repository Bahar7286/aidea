"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { AppShell } from "@/components/app/AppShell";
import { setSelectedFarmId } from "@/components/app/FarmSelector";
import {
  api,
  Device,
  DeviceCalibrateResult,
  Farm,
} from "@/lib/api";

export default function CalibrateDevicePage() {
  const params = useParams();
  const farmId = Number(params.id);
  const deviceId = Number(params.deviceId);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [device, setDevice] = useState<Device | null>(null);
  const [step, setStep] = useState(1);
  const [raw, setRaw] = useState<string>("");
  const [reference, setReference] = useState<string>("");
  const [result, setResult] = useState<DeviceCalibrateResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [tested, setTested] = useState(false);

  async function load() {
    const [f, d] = await Promise.all([
      api.getFarm(farmId),
      api.getDeviceDetail(deviceId),
    ]);
    setFarm(f);
    setDevice(d.device);
    if (d.device.last_moisture != null) {
      setRaw(String(d.device.last_moisture));
    }
  }

  useEffect(() => {
    if (!farmId || !deviceId) return;
    setSelectedFarmId(farmId);
    load().catch((err) => setError(err.message));
  }, [farmId, deviceId]);

  async function takeMeasurement() {
    setBusy(true);
    setError("");
    try {
      const reading = await api.iotSimulateForDevice(
        farmId,
        deviceId,
        "drought_risk",
      );
      setRaw(String(reading.soil_moisture));
      await load();
      setTested(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ölçüm alınamadı");
    } finally {
      setBusy(false);
    }
  }

  async function testLink() {
    setBusy(true);
    setError("");
    try {
      await api.testDevice(deviceId);
      setTested(true);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Test başarısız");
    } finally {
      setBusy(false);
    }
  }

  async function onSave(e: FormEvent) {
    e.preventDefault();
    const ref = Number(reference);
    if (Number.isNaN(ref) || ref < 0 || ref > 100) {
      setError("Referans değer 0–100 arasında olmalı.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const body: { reference_value: number; raw_value?: number } = {
        reference_value: ref,
      };
      if (raw !== "") body.raw_value = Number(raw);
      const res = await api.calibrateDevice(deviceId, body);
      setResult(res);
      setStep(4);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kalibrasyon başarısız");
    } finally {
      setBusy(false);
    }
  }

  const steps = ["Yerleştir", "Test et", "Referans", "Onayla"];
  const deviation =
    result?.deviation ??
    (raw !== "" && reference !== ""
      ? Number(raw) - Number(reference)
      : null);

  return (
    <AppShell title="Kurulum ve Kalibrasyon" farmName={farm?.name}>
      <div className="mb-4">
        <Link
          href={`/farms/${farmId}/devices/${deviceId}`}
          className="text-sm text-[var(--auth-forest)] hover:underline"
        >
          ← Cihaz detayı
        </Link>
      </div>

      <ol className="mb-6 grid grid-cols-4 gap-2">
        {steps.map((label, i) => {
          const n = i + 1;
          return (
            <li
              key={label}
              className={`rounded-xl px-2 py-3 text-center text-xs font-semibold ${
                step === n
                  ? "bg-[var(--auth-forest)] text-white"
                  : step > n
                    ? "bg-emerald-50 text-emerald-900"
                    : "bg-white text-[var(--auth-muted)] ring-1 ring-[var(--auth-border)]"
              }`}
            >
              {label}
            </li>
          );
        })}
      </ol>

      {error && (
        <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>
      )}

      <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
        <div className="app-surface space-y-4 p-4 sm:p-6">
          {step === 1 && (
            <>
              <p className="font-semibold">Fiziksel yerleştirme (rehber)</p>
              <div className="rounded-2xl bg-emerald-50/80 p-4 text-sm text-emerald-950">
                <p>
                  Sensörü bitki kök bölgesine yakın, yaklaşık{" "}
                  <strong>{device?.depth_cm ?? 20} cm</strong> derinliğe
                  yerleştirin. Kabloyu gerilimsiz bırakın.
                </p>
                <p className="mt-2 text-xs opacity-80">
                  Bu adım MVP’de kontrol listesidir; donanım bağlı değildir.
                </p>
              </div>
              <ul className="space-y-2 text-sm">
                {["Probe yerleştirildi", "Kablo kontrolü", "Bağlantı hazır"].map(
                  (item) => (
                    <li key={item} className="flex items-center gap-2">
                      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-600 text-[10px] text-white">
                        ✓
                      </span>
                      {item}
                    </li>
                  ),
                )}
              </ul>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setStep(2)}
              >
                Teste geç
              </button>
            </>
          )}

          {step === 2 && (
            <>
              <p className="font-semibold">Bağlantıyı test et</p>
              <p className="text-sm text-[var(--auth-muted)]">
                Simülasyon bağlantı testi sinyal ve senkron zamanını günceller.
              </p>
              {tested ? (
                <p className="rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
                  Bağlantı testi başarılı
                  {device?.signal_dbm != null
                    ? ` · ${device.signal_dbm} dBm`
                    : ""}
                </p>
              ) : (
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={testLink}
                  disabled={busy}
                >
                  {busy ? "…" : "Testi başlat"}
                </button>
              )}
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setStep(3)}
                disabled={!tested}
              >
                Referansa geç
              </button>
            </>
          )}

          {(step === 3 || step === 4) && (
            <form className="space-y-4" onSubmit={onSave}>
              <p className="font-semibold">Referans değer</p>
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="label" htmlFor="raw">
                    Ham değer (%)
                  </label>
                  <div className="flex gap-2">
                    <input
                      id="raw"
                      className="input"
                      type="number"
                      step="0.1"
                      min={0}
                      max={100}
                      value={raw}
                      onChange={(e) => setRaw(e.target.value)}
                    />
                    <button
                      type="button"
                      className="btn btn-secondary shrink-0 text-sm"
                      onClick={takeMeasurement}
                      disabled={busy}
                    >
                      Ölçüm al
                    </button>
                  </div>
                </div>
                <div>
                  <label className="label" htmlFor="ref">
                    Referans değer gir
                  </label>
                  <input
                    id="ref"
                    className="input"
                    type="number"
                    step="0.1"
                    min={0}
                    max={100}
                    value={reference}
                    onChange={(e) => setReference(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="overflow-x-auto rounded-xl ring-1 ring-[var(--auth-border)]">
                <table className="w-full min-w-[360px] text-left text-sm">
                  <thead className="bg-slate-50 text-xs text-[var(--auth-muted)]">
                    <tr>
                      <th className="px-3 py-2">Ham</th>
                      <th className="px-3 py-2">Referans</th>
                      <th className="px-3 py-2">Sapma</th>
                      <th className="px-3 py-2">Durum</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="px-3 py-2">
                        {result?.raw_value ?? (raw || "—")}
                      </td>
                      <td className="px-3 py-2">
                        {result?.reference_value ?? (reference || "—")}
                      </td>
                      <td className="px-3 py-2">
                        {deviation != null && !Number.isNaN(deviation)
                          ? deviation.toFixed(2)
                          : "—"}
                      </td>
                      <td className="px-3 py-2">
                        {result ? (
                          <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
                            {result.status === "good"
                              ? "İyi"
                              : result.status === "ok"
                                ? "Kabul"
                                : "Dikkat"}
                          </span>
                        ) : (
                          "—"
                        )}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {result && (
                <p className="text-sm text-[var(--auth-muted)]">
                  {result.message} Ofset: {result.calibration_offset}
                </p>
              )}

              <div className="flex flex-wrap gap-2">
                {step === 3 && (
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={busy}
                  >
                    {busy ? "…" : "Kalibrasyonu kaydet"}
                  </button>
                )}
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={takeMeasurement}
                  disabled={busy}
                >
                  Tekrar ölç
                </button>
                {step === 4 && (
                  <Link
                    href={`/farms/${farmId}/devices/${deviceId}`}
                    className="btn btn-primary"
                  >
                    Cihaza dön
                  </Link>
                )}
              </div>
            </form>
          )}
        </div>

        <aside className="app-surface h-fit space-y-2 p-4 text-xs text-[var(--auth-muted)]">
          <p className="text-sm font-semibold text-[var(--auth-ink)]">
            {device?.device_name || "Cihaz"}
          </p>
          <p>
            Kalibrasyon MVP’de yazılım ofseti olarak saklanır; sonraki
            simülasyon/ingest okumalarına uygulanır.
          </p>
          <p>
            Veri kaynağı her zaman etiketlenir:{" "}
            <strong>simulation</strong>
          </p>
        </aside>
      </div>
    </AppShell>
  );
}
