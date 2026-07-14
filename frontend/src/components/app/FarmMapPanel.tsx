"use client";

import dynamic from "next/dynamic";
import { SourceBadge } from "@/components/app/SourceBadge";
import type { MapZone } from "@/components/app/FarmLeafletMap";

const FarmLeafletMap = dynamic(
  () =>
    import("@/components/app/FarmLeafletMap").then((m) => m.FarmLeafletMap),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-64 items-center justify-center bg-emerald-950/20 text-sm text-white/70 sm:h-80">
        Harita yükleniyor…
      </div>
    ),
  },
);

/** Turkey center fallback when farm has no coords. */
export const TURKEY_CENTER = { lat: 39.0, lng: 35.0 };
export const SERIK_DEMO = { lat: 36.9167, lng: 31.1 };

export function resolveFarmCoords(farm?: {
  latitude?: number | null;
  longitude?: number | null;
  location?: string | null;
  name?: string | null;
} | null): { lat: number; lng: number; source: string } {
  if (
    farm?.latitude != null &&
    farm?.longitude != null &&
    Number.isFinite(farm.latitude) &&
    Number.isFinite(farm.longitude)
  ) {
    return { lat: farm.latitude, lng: farm.longitude, source: "stored" };
  }
  const name = (farm?.name || "").toLowerCase();
  if (name.includes("domates")) {
    return { ...SERIK_DEMO, source: "demo" };
  }
  const loc = (farm?.location || "").toLowerCase();
  if (loc.includes("antalya") || loc.includes("serik")) {
    return { ...SERIK_DEMO, source: "hint" };
  }
  if (loc.includes("konya") || loc.includes("karap")) {
    return { lat: 37.7147, lng: 33.5506, source: "hint" };
  }
  if (loc.includes("ısparta") || loc.includes("isparta") || loc.includes("yalvaç") || loc.includes("yalvac")) {
    return { lat: 38.2956, lng: 31.1778, source: "hint" };
  }
  if (loc.includes("gelendost")) {
    return { lat: 38.1210, lng: 31.0150, source: "hint" };
  }
  if (loc.includes("ankara") || loc.includes("gölbaşı") || loc.includes("golbasi")) {
    return { lat: 39.7900, lng: 32.8050, source: "hint" };
  }
  return { ...TURKEY_CENTER, source: "turkey" };
}

export function FarmMapPanel({
  farm,
  zones,
  areaDa,
  sourceType,
  title = "Arazi haritası",
  subtitle,
  heightClass,
  interactive = true,
}: {
  farm?: {
    latitude?: number | null;
    longitude?: number | null;
    location?: string | null;
    name?: string | null;
    area?: number | null;
    geometry_geojson?: string | null;
  } | null;
  zones: MapZone[];
  areaDa?: number | null;
  sourceType?: string | null;
  title?: string;
  subtitle?: string;
  heightClass?: string;
  interactive?: boolean;
}) {
  const { lat, lng } = resolveFarmCoords(farm);
  const area = areaDa ?? farm?.area ?? 2;
  const haLabel = (Math.max(0.5, area) / 10).toFixed(area >= 10 ? 1 : 2);
  const hasParcel = !!farm?.geometry_geojson;

  return (
    <div className="overflow-hidden rounded-2xl border border-[var(--auth-border)] bg-white shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--auth-border)] px-4 py-2.5">
        <div>
          <p className="text-sm font-semibold">{title}</p>
          {subtitle && (
            <p className="text-[10px] text-[var(--auth-muted)]">{subtitle}</p>
          )}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-700">
            {Number(area).toFixed(1)} da · ~{haLabel} ha
          </span>
          {hasParcel && (
            <span className="rounded-full bg-lime-50 px-2 py-0.5 text-[10px] font-medium text-lime-800">
              Parsel sınırı
            </span>
          )}
          <SourceBadge source={sourceType || "simulation"} />
          <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-[var(--auth-forest)]">
            OSM
          </span>
        </div>
      </div>
      <FarmLeafletMap
        latitude={lat}
        longitude={lng}
        zones={zones}
        areaDa={area}
        heightClass={heightClass || "h-64 sm:h-80"}
        interactive={interactive}
        geometryGeoJson={farm?.geometry_geojson}
      />
    </div>
  );
}
