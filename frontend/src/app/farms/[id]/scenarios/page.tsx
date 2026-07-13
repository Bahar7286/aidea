"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { AppShell } from "@/components/app/AppShell";
import { FarmSelector, setSelectedFarmId } from "@/components/app/FarmSelector";
import {
  api,
  CustomSimulateResult,
  Farm,
  ScenarioCompare,
} from "@/lib/api";

export default function ScenariosPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [name, setName] = useState("Özel sulama senaryosu");
  const [duration, setDuration] = useState(60);
  const [water, setWater] = useState(360);
  const [target, setTarget] = useState(45);
  const [custom, setCustom] = useState<CustomSimulateResult | null>(null);
  const [compare, setCompare] = useState<ScenarioCompare | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!farmId) return;
    setSelectedFarmId(farmId);
    api.getFarm(farmId).then(setFarm).catch((err) => setError(err.message));
  }, [farmId]);

  async function runCustom(e?: FormEvent) {
    e?.preventDefault();
    setBusy(true);
    setError("");
    try {
      const res = await api.customSimulate({
        farm_id: farmId,
        duration_minutes: duration,
        water_amount_liters: water,
        target_moisture: target,
        name,
      });
      setCustom(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Simülasyon başarısız");
    } finally {
      setBusy(false);
    }
  }

  async function runCompare() {
    setBusy(true);
    setError("");
    try {
      const res = await api.compareScenarios(
        farmId,
        ["irrigate_now", "wait_12h", "wait_24h", "skip"],
        duration,
      );
      setCompare(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Karşılaştırma başarısız");
    } finally {
      setBusy(false);
    }
  }

  function reset() {
    setDuration(60);
    setWater(360);
    setTarget(45);
    setCustom(null);
  }

  const forecast = custom?.forecast || [];

  return (
    <AppShell title="Sulama Senaryo Simülatörü" farmName={farm?.name}>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <FarmSelector farmId={farmId} suffixPath="/scenarios" />
        <Link href={`/farms/${farmId}/ai`} className="btn btn-ghost text-sm">
          AI önerileri
        </Link>
      </div>

      {error && (
        <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <form className="app-surface space-y-4 p-4" onSubmit={runCustom}>
          <div>
            <label className="label" htmlFor="name">
              Senaryo adı
            </label>
            <input
              id="name"
              className="input"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div>
            <label className="label" htmlFor="dur">
              Sulama süresi: {duration} dk
            </label>
            <input
              id="dur"
              type="range"
              min={10}
              max={180}
              value={duration}
              onChange={(e) => {
                const v = Number(e.target.value);
                setDuration(v);
                setWater(Math.round(v * 6));
              }}
              className="w-full"
            />
          </div>
          <div>
            <label className="label" htmlFor="water">
              Su miktarı: {water} L
            </label>
            <input
              id="water"
              type="range"
              min={50}
              max={1200}
              step={10}
              value={water}
              onChange={(e) => setWater(Number(e.target.value))}
              className="w-full"
            />
          </div>
          <div>
            <label className="label" htmlFor="target">
              Hedef toprak nemi: %{target}
            </label>
            <input
              id="target"
              type="range"
              min={15}
              max={70}
              value={target}
              onChange={(e) => setTarget(Number(e.target.value))}
              className="w-full"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="submit" className="btn btn-primary" disabled={busy}>
              {busy ? "…" : "Simülasyonu çalıştır"}
            </button>
            <button type="button" className="btn btn-secondary" onClick={reset}>
              Sıfırla
            </button>
            <button
              type="button"
              className="btn btn-ghost text-sm"
              onClick={runCompare}
              disabled={busy}
            >
              Hazır senaryoları karşılaştır
            </button>
          </div>
        </form>

        <div className="space-y-4">
          {custom && (
            <div className="app-surface grid grid-cols-2 gap-3 p-4 sm:grid-cols-4">
              <div>
                <p className="text-[11px] text-[var(--auth-muted)]">Tahmini nem</p>
                <p className="text-lg font-bold">%{custom.estimated_moisture}</p>
              </div>
              <div>
                <p className="text-[11px] text-[var(--auth-muted)]">Su</p>
                <p className="text-lg font-bold">
                  {custom.estimated_water_mm} mm
                </p>
              </div>
              <div>
                <p className="text-[11px] text-[var(--auth-muted)]">Maliyet</p>
                <p className="text-lg font-bold">
                  ₺{custom.estimated_cost_try}
                </p>
              </div>
              <div>
                <p className="text-[11px] text-[var(--auth-muted)]">Risk</p>
                <p className="text-lg font-bold">{custom.risk_level}</p>
              </div>
              <p className="col-span-full text-xs text-[var(--auth-muted)]">
                {custom.explanation}
              </p>
            </div>
          )}

          {forecast.length > 0 && (
            <div className="app-surface p-4">
              <p className="mb-2 text-sm font-semibold">Tahmini toprak nemi (5 gün)</p>
              <svg viewBox="0 0 480 180" className="h-44 w-full">
                <polyline
                  fill="none"
                  stroke="#94a3b8"
                  strokeWidth="2"
                  points={forecast
                    .map(
                      (f, i) =>
                        `${20 + (i / 5) * 440},${160 - f.current_path * 1.4}`,
                    )
                    .join(" ")}
                />
                <polyline
                  fill="none"
                  stroke="#1b4332"
                  strokeWidth="2.5"
                  points={forecast
                    .map(
                      (f, i) =>
                        `${20 + (i / 5) * 440},${160 - f.scenario_path * 1.4}`,
                    )
                    .join(" ")}
                />
                <line
                  x1="20"
                  x2="460"
                  y1={160 - 20 * 1.4}
                  y2={160 - 20 * 1.4}
                  stroke="#dc2626"
                  strokeDasharray="4 4"
                  strokeWidth="1.5"
                />
              </svg>
              <div className="flex gap-4 text-[10px] text-[var(--auth-muted)]">
                <span>Gri: mevcut gidiş</span>
                <span>Yeşil: senaryo</span>
                <span>Kırmızı: kritik %20</span>
              </div>
            </div>
          )}

          {compare && (
            <div className="app-surface overflow-x-auto p-2">
              <table className="w-full min-w-[480px] text-left text-sm">
                <thead className="text-xs text-[var(--auth-muted)]">
                  <tr>
                    <th className="px-2 py-2">Senaryo</th>
                    <th className="px-2 py-2">Nem</th>
                    <th className="px-2 py-2">Su L</th>
                    <th className="px-2 py-2">Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {compare.results.map((r) => (
                    <tr
                      key={r.scenario}
                      className={
                        r.recommended ? "bg-emerald-50 font-semibold" : ""
                      }
                    >
                      <td className="px-2 py-2">{r.label}</td>
                      <td className="px-2 py-2">%{r.estimated_moisture}</td>
                      <td className="px-2 py-2">
                        {r.estimated_water_liters ?? "—"}
                      </td>
                      <td className="px-2 py-2">{r.risk_level}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
