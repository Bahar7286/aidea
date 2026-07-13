"use client";

import { useMemo, useState } from "react";

export type TwinZone = {
  id?: number | null;
  name: string;
  soil_moisture?: number | null;
  soil_temperature?: number | null;
  air_temperature?: number | null;
  air_humidity?: number | null;
  ec?: number | null;
  risk?: string;
};

const LAYERS = [
  { key: "moisture", label: "Toprak nemi" },
  { key: "soil_temp", label: "Toprak sıcaklığı" },
  { key: "air_temp", label: "Hava sıcaklığı" },
  { key: "humidity", label: "Hava nemi" },
  { key: "ec", label: "EC" },
] as const;

function tone(m: number | null | undefined) {
  if (m == null) return "bg-slate-400/70";
  if (m < 22) return "bg-orange-500/90";
  if (m < 28) return "bg-amber-400/90";
  return "bg-emerald-500/85";
}

export function TwinMapPanel({
  zones,
  selectedName,
  onSelect,
  insight,
  sourceLabel,
  confidence,
}: {
  zones: TwinZone[];
  selectedName?: string;
  onSelect?: (z: TwinZone) => void;
  insight?: string | null;
  sourceLabel?: string | null;
  confidence?: number | null;
}) {
  const [layers, setLayers] = useState<Record<string, boolean>>({
    moisture: true,
    soil_temp: false,
    air_temp: false,
    humidity: false,
    ec: false,
  });

  const selected = useMemo(
    () => zones.find((z) => z.name === selectedName) || zones[0],
    [zones, selectedName],
  );

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
      <div className="app-surface overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--auth-border)] px-4 py-2.5">
          <div>
            <p className="text-sm font-semibold">Dijital ikiz haritası</p>
            <p className="text-[10px] text-[var(--auth-muted)]">
              Sınırlı viz — uydu değil ·{" "}
              {sourceLabel ? `Kaynak: ${sourceLabel}` : "veri yok"}
            </p>
          </div>
          <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
            Canlı
          </span>
        </div>
        <div className="relative aspect-[5/4] bg-gradient-to-br from-[#2d4a32] via-[#5a7a45] to-[#9cb37a] p-3 sm:p-5">
          <div className="absolute left-3 top-3 z-10 flex flex-col gap-1">
            <button type="button" className="rounded bg-white/90 px-2 py-1 text-xs shadow">
              +
            </button>
            <button type="button" className="rounded bg-white/90 px-2 py-1 text-xs shadow">
              −
            </button>
          </div>
          <div className="grid h-full grid-cols-1 gap-2 sm:grid-cols-3">
            {zones.slice(0, 3).map((z) => (
              <button
                key={z.name}
                type="button"
                onClick={() => onSelect?.(z)}
                className={`relative flex flex-col justify-between rounded-2xl border p-3 text-left text-white shadow-md transition ${tone(
                  z.soil_moisture,
                )} ${
                  selected?.name === z.name
                    ? "border-white ring-2 ring-white"
                    : "border-white/30"
                }`}
              >
                <span className="text-xs font-semibold drop-shadow">{z.name}</span>
                {layers.moisture && (
                  <span className="text-2xl font-bold drop-shadow">
                    {z.soil_moisture != null ? `%${z.soil_moisture}` : "—"}
                  </span>
                )}
                <span className="absolute right-2 top-2 h-2.5 w-2.5 rounded-full bg-sky-300 shadow" />
              </button>
            ))}
          </div>
          <div className="absolute bottom-3 left-3 right-3 h-1.5 overflow-hidden rounded-full bg-black/25">
            <div className="h-full w-2/3 rounded-full bg-white/70" />
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <div className="app-surface space-y-2 p-4">
          <p className="text-sm font-semibold">Katmanlar</p>
          {LAYERS.map((l) => (
            <label key={l.key} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                className="accent-[var(--auth-forest)]"
                checked={!!layers[l.key]}
                onChange={(e) =>
                  setLayers((prev) => ({ ...prev, [l.key]: e.target.checked }))
                }
              />
              {l.label}
            </label>
          ))}
          <div className="flex justify-between pt-2 text-[10px] text-[var(--auth-muted)]">
            <span>Düşük</span>
            <span className="h-2 flex-1 mx-2 rounded-full bg-gradient-to-r from-orange-500 via-amber-300 to-emerald-500" />
            <span>Yüksek</span>
          </div>
        </div>

        {selected && (
          <div className="app-surface space-y-2 p-4">
            <p className="text-sm font-semibold">Seçili bölge: {selected.name}</p>
            <ul className="space-y-1 text-sm text-[var(--auth-muted)]">
              <li>Nem: {selected.soil_moisture != null ? `%${selected.soil_moisture}` : "—"}</li>
              <li>
                Toprak °C: {selected.soil_temperature ?? "—"} · Hava °C:{" "}
                {selected.air_temperature ?? "—"}
              </li>
              <li>
                Hava nemi: {selected.air_humidity ?? "—"} · EC: {selected.ec ?? "—"}
              </li>
              <li>
                Güven: {confidence != null ? `%${Math.round(confidence)}` : "—"}
              </li>
            </ul>
          </div>
        )}

        <div className="rounded-2xl border border-emerald-200 bg-emerald-50/80 p-4 text-sm">
          <p className="font-semibold text-[var(--auth-forest)]">AI içgörüsü</p>
          <p className="mt-1 text-[var(--auth-muted)]">
            {insight || "Analiz için veri girin."}
          </p>
        </div>
      </div>
    </div>
  );
}
