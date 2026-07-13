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

function toneHex(m: number | null | undefined) {
  if (m == null) return "#94a3b8";
  if (m < 22) return "#f97316";
  if (m < 28) return "#fbbf24";
  return "#22c55e";
}

export function TwinMapPanel({
  zones,
  selectedName,
  onSelect,
  insight,
  sourceLabel,
  confidence,
  areaDa,
}: {
  zones: TwinZone[];
  selectedName?: string;
  onSelect?: (z: TwinZone) => void;
  insight?: string | null;
  sourceLabel?: string | null;
  confidence?: number | null;
  areaDa?: number | null;
}) {
  const [layers, setLayers] = useState<Record<string, boolean>>({
    moisture: true,
    soil_temp: false,
    air_temp: false,
    humidity: false,
    ec: false,
  });
  const [zoom, setZoom] = useState(1);

  const selected = useMemo(
    () => zones.find((z) => z.name === selectedName) || zones[0],
    [zones, selectedName],
  );

  const area = Math.max(0.5, areaDa ?? 2);
  const scale = Math.min(1.4, Math.max(0.55, Math.sqrt(area / 2))) * zoom;
  const cols = Math.min(3, Math.max(1, zones.length || 1));
  const aspect =
    area >= 8 ? "aspect-[16/9]" : area >= 4 ? "aspect-[5/3]" : "aspect-[5/4]";
  const haLabel = (area / 10).toFixed(area >= 10 ? 1 : 2);

  const plot = zones.slice(0, cols);
  const display =
    plot.length > 0
      ? plot
      : [
          { name: "Bölge A", soil_moisture: null },
          { name: "Bölge B", soil_moisture: null },
          { name: "Bölge C", soil_moisture: null },
        ];

  function slicePath(i: number, n: number) {
    const pad = 6;
    const w = 100 - pad * 2;
    const h = 100 - pad * 2;
    const sliceW = w / n;
    const x0 = pad + i * sliceW;
    const x1 = x0 + sliceW;
    const tw = (i % 2 === 0 ? 2.5 : -2) * (scale / zoom);
    const bw = (i % 2 === 0 ? -3 : 2.5) * (scale / zoom);
    return `M ${x0 + 1} ${pad + tw} L ${x1 - 1} ${pad - tw * 0.4} L ${x1 + bw * 0.25} ${pad + h + bw} L ${x0 - bw * 0.2} ${pad + h - bw * 0.35} Z`;
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_300px]">
      <div className="app-surface overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--auth-border)] px-4 py-2.5">
          <div>
            <p className="text-sm font-semibold">Dijital ikiz haritası</p>
            <p className="text-[10px] text-[var(--auth-muted)]">
              Şematik viz — uydu değil · {area.toFixed(1)} da (~{haLabel} ha) ·{" "}
              {sourceLabel ? `Kaynak: ${sourceLabel}` : "veri yok"}
            </p>
          </div>
          <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
            Simüle IoT
          </span>
        </div>
        <div
          className={`relative ${aspect} bg-gradient-to-br from-[#2d4a32] via-[#5a7a45] to-[#9cb37a] p-3 sm:p-5`}
        >
          <div className="absolute left-3 top-3 z-10 flex flex-col gap-1">
            <button
              type="button"
              className="rounded bg-white/90 px-2 py-1 text-xs shadow"
              onClick={() => setZoom((z) => Math.min(1.6, z + 0.12))}
            >
              +
            </button>
            <button
              type="button"
              className="rounded bg-white/90 px-2 py-1 text-xs shadow"
              onClick={() => setZoom((z) => Math.max(0.7, z - 0.12))}
            >
              −
            </button>
          </div>
          <div
            className="mx-auto h-full transition-transform duration-500 ease-out"
            style={{ width: `${Math.round(scale * 92)}%`, maxWidth: "100%" }}
          >
            <svg viewBox="0 0 100 100" className="h-full w-full drop-shadow-lg">
              {display.map((z, i) => {
                const active = selected?.name === z.name;
                return (
                  <g
                    key={z.name}
                    role="button"
                    tabIndex={0}
                    className="cursor-pointer"
                    onClick={() => onSelect?.(z as TwinZone)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") onSelect?.(z as TwinZone);
                    }}
                  >
                    <path
                      d={slicePath(i, display.length)}
                      fill={toneHex(z.soil_moisture)}
                      fillOpacity={0.9}
                      stroke={active ? "#fff" : "rgba(255,255,255,0.4)"}
                      strokeWidth={active ? 1.4 : 0.55}
                    />
                    <text
                      x={6 + ((88 / display.length) * (i + 0.5))}
                      y={26}
                      textAnchor="middle"
                      fill="#fff"
                      style={{ fontSize: 3.8, fontWeight: 700 }}
                    >
                      {z.name}
                    </text>
                    {layers.moisture && (
                      <text
                        x={6 + ((88 / display.length) * (i + 0.5))}
                        y={40}
                        textAnchor="middle"
                        fill="#fff"
                        style={{ fontSize: 7, fontWeight: 800 }}
                      >
                        {z.soil_moisture != null ? `%${z.soil_moisture}` : "—"}
                      </text>
                    )}
                    <circle
                      cx={6 + ((88 / display.length) * (i + 0.72))}
                      cy={18}
                      r={1.4}
                      fill="#7dd3fc"
                    />
                  </g>
                );
              })}
            </svg>
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
            <span className="mx-2 h-2 flex-1 rounded-full bg-gradient-to-r from-orange-500 via-amber-300 to-emerald-500" />
            <span>Yüksek</span>
          </div>
        </div>

        {selected && (
          <div className="app-surface space-y-2 p-4">
            <p className="text-sm font-semibold">Seçili bölge: {selected.name}</p>
            <ul className="space-y-1 text-sm text-[var(--auth-muted)]">
              <li>
                Nem:{" "}
                {selected.soil_moisture != null ? `%${selected.soil_moisture}` : "—"}
              </li>
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
