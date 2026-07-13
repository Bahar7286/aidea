"use client";

import dynamic from "next/dynamic";
import { SERIK_DEMO } from "@/components/app/FarmMapPanel";

const FarmLeafletMap = dynamic(
  () =>
    import("@/components/app/FarmLeafletMap").then((m) => m.FarmLeafletMap),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-44 w-full items-center justify-center rounded-2xl bg-black/20 text-xs text-white/70">
        Arazi haritası…
      </div>
    ),
  },
);

/** Rich OSM field preview on auth/login left panel (demo Antalya/Serik). */
export function AuthFieldVisual() {
  return (
    <div
      className="auth-field-visual relative mb-6 overflow-hidden rounded-2xl border border-white/20 shadow-inner"
      aria-hidden
    >
      <FarmLeafletMap
        latitude={SERIK_DEMO.lat}
        longitude={SERIK_DEMO.lng}
        areaDa={2.5}
        heightClass="h-44"
        interactive={false}
        zones={[
          { name: "Kuzey", moisture: 24 },
          { name: "Orta", moisture: 31 },
          { name: "Güney", moisture: 28 },
        ]}
      />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 flex items-center justify-between gap-2 bg-gradient-to-t from-black/55 to-transparent px-3 pb-2.5 pt-8 text-[10px] font-medium text-white/90">
        <span>OpenStreetMap · Antalya / Serik demo</span>
        <span className="tabular-nums text-lime-200/90">nem katmanı</span>
      </div>
    </div>
  );
}
