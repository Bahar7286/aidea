"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { AppShell } from "@/components/app/AppShell";
import { FarmSelector, setSelectedFarmId } from "@/components/app/FarmSelector";
import { api, Farm, ManagementZone } from "@/lib/api";

const STEPS = ["Temel", "Ölçümler", "Sulama", "Özet"];

export default function ManualDataPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const router = useRouter();
  const [farm, setFarm] = useState<Farm | null>(null);
  const [zones, setZones] = useState<ManagementZone[]>([]);
  const [step, setStep] = useState(0);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    zone_id: "",
    soil_moisture: "34",
    soil_moisture_deep: "38",
    soil_temperature: "25",
    air_temperature: "33",
    air_humidity: "42",
    rainfall_probability: "5",
    last_irrigation_hours_ago: "36",
    ec: "",
    notes: "",
  });

  useEffect(() => {
    if (!farmId) return;
    setSelectedFarmId(farmId);
    Promise.all([api.getFarm(farmId), api.listZones(farmId)])
      .then(([f, z]) => {
        setFarm(f);
        setZones(z);
      })
      .catch((err) => setError(err.message));
  }, [farmId]);

  function set(key: string, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (step < 3) {
      setStep((s) => s + 1);
      return;
    }
    setLoading(true);
    setError("");
    try {
      await api.createReading(farmId, {
        soil_moisture: Number(form.soil_moisture),
        soil_moisture_deep: form.soil_moisture_deep
          ? Number(form.soil_moisture_deep)
          : null,
        soil_temperature: Number(form.soil_temperature || 25),
        air_temperature: Number(form.air_temperature),
        air_humidity: Number(form.air_humidity || 42),
        rainfall_probability: Number(form.rainfall_probability),
        last_irrigation_hours_ago: Number(form.last_irrigation_hours_ago),
        ec: form.ec ? Number(form.ec) : null,
        zone_id: form.zone_id ? Number(form.zone_id) : null,
        source_type: "manual",
      });
      await api.predict(farmId);
      router.push(`/farms/${farmId}/sensors/live`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kayıt başarısız");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell title="Manuel Veri Girişi" farmName={farm?.name}>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <FarmSelector farmId={farmId} suffixPath="/data/manual" />
        <p className="text-xs text-[var(--auth-muted)]">
          Kaynak etiketi: <strong>manual</strong>
        </p>
      </div>

      <ol className="mb-6 grid grid-cols-4 gap-2">
        {STEPS.map((label, i) => (
          <li key={label} className="text-center">
            <span
              className={`mx-auto flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${
                i <= step
                  ? "bg-[var(--auth-forest)] text-white"
                  : "bg-[var(--auth-border)] text-[var(--auth-muted)]"
              }`}
            >
              {i + 1}
            </span>
            <span className="mt-1 hidden text-[10px] sm:block">{label}</span>
          </li>
        ))}
      </ol>

      <form onSubmit={onSubmit} className="mx-auto max-w-xl space-y-4">
        <div className="app-surface space-y-3 p-5">
          {step === 0 && (
            <>
              <h2 className="font-semibold">Temel bilgiler</h2>
              <div>
                <label className="label">Bölge (opsiyonel)</label>
                <select
                  className="input"
                  value={form.zone_id}
                  onChange={(e) => set("zone_id", e.target.value)}
                >
                  <option value="">Arazi geneli</option>
                  {zones.map((z) => (
                    <option key={z.id} value={z.id}>
                      {z.name}
                    </option>
                  ))}
                </select>
              </div>
              <p className="text-xs text-[var(--auth-muted)]">
                Zaman damgası kayıt anında otomatik atanır.
              </p>
            </>
          )}

          {step === 1 && (
            <>
              <h2 className="font-semibold">Ölçümler</h2>
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="label">Toprak nemi % *</label>
                  <input
                    className="input"
                    type="number"
                    step="0.1"
                    required
                    value={form.soil_moisture}
                    onChange={(e) => set("soil_moisture", e.target.value)}
                  />
                  <p className="mt-1 text-[10px] text-[var(--auth-muted)]">
                    Önerilen: %25–35
                  </p>
                </div>
                <div>
                  <label className="label">Derin nem %</label>
                  <input
                    className="input"
                    type="number"
                    step="0.1"
                    value={form.soil_moisture_deep}
                    onChange={(e) => set("soil_moisture_deep", e.target.value)}
                  />
                </div>
                <div>
                  <label className="label">Toprak °C</label>
                  <input
                    className="input"
                    type="number"
                    step="0.1"
                    value={form.soil_temperature}
                    onChange={(e) => set("soil_temperature", e.target.value)}
                  />
                </div>
                <div>
                  <label className="label">Hava °C *</label>
                  <input
                    className="input"
                    type="number"
                    step="0.1"
                    required
                    value={form.air_temperature}
                    onChange={(e) => set("air_temperature", e.target.value)}
                  />
                </div>
                <div>
                  <label className="label">Hava nemi %</label>
                  <input
                    className="input"
                    type="number"
                    value={form.air_humidity}
                    onChange={(e) => set("air_humidity", e.target.value)}
                  />
                </div>
                <div>
                  <label className="label">EC</label>
                  <input
                    className="input"
                    type="number"
                    step="0.01"
                    value={form.ec}
                    onChange={(e) => set("ec", e.target.value)}
                  />
                </div>
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <h2 className="font-semibold">Sulama / yağış</h2>
              <div>
                <label className="label">Yağış ihtimali % *</label>
                <input
                  className="input"
                  type="number"
                  required
                  value={form.rainfall_probability}
                  onChange={(e) => set("rainfall_probability", e.target.value)}
                />
              </div>
              <div>
                <label className="label">Son sulama (saat önce) *</label>
                <input
                  className="input"
                  type="number"
                  required
                  value={form.last_irrigation_hours_ago}
                  onChange={(e) =>
                    set("last_irrigation_hours_ago", e.target.value)
                  }
                />
              </div>
              <div>
                <label className="label">Not (opsiyonel)</label>
                <textarea
                  className="input min-h-[80px]"
                  value={form.notes}
                  onChange={(e) => set("notes", e.target.value)}
                />
              </div>
            </>
          )}

          {step === 3 && (
            <>
              <h2 className="font-semibold">Özet</h2>
              <ul className="space-y-1 text-sm text-[var(--auth-muted)]">
                <li>
                  Nem %{form.soil_moisture}
                  {form.soil_moisture_deep
                    ? ` / derin %${form.soil_moisture_deep}`
                    : ""}
                </li>
                <li>
                  Hava {form.air_temperature}°C · Yağış %{form.rainfall_probability}
                </li>
                <li>Son sulama: {form.last_irrigation_hours_ago} sa önce</li>
                <li>Kaynak: manual</li>
              </ul>
            </>
          )}

          {error && <p className="text-sm text-[var(--risk-critical)]">{error}</p>}

          <div className="flex flex-wrap gap-2 pt-2">
            <Link href={`/farms/${farmId}`} className="btn btn-ghost">
              İptal
            </Link>
            {step > 0 && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setStep((s) => s - 1)}
              >
                Geri
              </button>
            )}
            <button className="btn btn-primary flex-1" disabled={loading}>
              {step < 3
                ? "Devam Et"
                : loading
                  ? "Kaydediliyor..."
                  : "Kaydet ve analiz et"}
            </button>
          </div>
        </div>
      </form>
    </AppShell>
  );
}
