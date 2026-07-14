"use client";

import { useMemo, useState } from "react";
import { FarmMapPanel } from "@/components/app/FarmMapPanel";
import { SourceBadge } from "@/components/app/SourceBadge";

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

export function TwinMapPanel({
  farm,
  zones,
  selectedName,
  onSelect,
  insight,
  sourceLabel,
  confidence,
  areaDa,
}: {
  farm?: {
    latitude?: number | null;
    longitude?: number | null;
    location?: string | null;
    name?: string | null;
    area?: number | null;
    geometry_geojson?: string | null;
  } | null;
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

  const selected = useMemo(
    () => zones.find((z) => z.name === selectedName) || zones[0],
    [zones, selectedName],
  );

  const mapZones = (
    zones.length
      ? zones
      : [
          { name: "Bölge A", soil_moisture: null },
          { name: "Bölge B", soil_moisture: null },
          { name: "Bölge C", soil_moisture: null },
        ]
  ).map((z) => ({
    name: z.name,
    moisture: layers.moisture ? z.soil_moisture : null,
  }));

  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_300px]">
      <div className="space-y-3">
        <FarmMapPanel
          farm={farm}
          zones={mapZones}
          areaDa={areaDa ?? farm?.area}
          sourceType={sourceLabel || "simulation"}
          title="Dijital ikiz haritası"
          subtitle={`OSM · ${farm?.geometry_geojson ? "parsel sınırı" : "nem poligonları"} · ${sourceLabel ? `Kaynak: ${sourceLabel}` : "veri yok"}`}
          heightClass="h-[22rem] sm:h-[28rem]"
        />
        <div className="flex flex-wrap gap-2 px-1">
          {zones.map((z) => (
            <button
              key={z.name}
              type="button"
              onClick={() => onSelect?.(z)}
              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                selected?.name === z.name
                  ? "bg-[var(--auth-forest)] text-white"
                  : "bg-white text-[var(--auth-muted)] ring-1 ring-[var(--auth-border)]"
              }`}
            >
              {z.name}
              {z.soil_moisture != null ? ` · %${z.soil_moisture}` : ""}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        <div className="app-surface space-y-2 p-4">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-semibold">Katmanlar</p>
            <SourceBadge source={sourceLabel || "simulation"} />
          </div>
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
