"use client";

import dynamic from "next/dynamic";
import { SERIK_DEMO } from "@/components/app/FarmMapPanel";

const FarmLeafletMap = dynamic(
  () =>
    import("@/components/app/FarmLeafletMap").then((m) => m.FarmLeafletMap),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full min-h-[16rem] w-full items-center justify-center bg-black/25 text-sm text-white/70 sm:min-h-[20rem] lg:min-h-[24rem]">
        Arazi görünümü…
      </div>
    ),
  },
);

/** Edge-to-edge field/map visual for marketing landing hero. */
export function LandingFieldHero() {
  return (
    <div className="landing-hero-frame relative h-full min-h-[16rem] overflow-hidden rounded-[1.75rem] border border-white/20 shadow-[0_24px_60px_-20px_rgba(0,0,0,0.55)] sm:min-h-[20rem] lg:min-h-[24rem]">
      <FarmLeafletMap
        latitude={SERIK_DEMO.lat}
        longitude={SERIK_DEMO.lng}
        areaDa={2.5}
        heightClass="h-full min-h-[16rem] sm:min-h-[20rem] lg:min-h-[24rem]"
        interactive={false}
        zones={[
          { name: "Kuzey", moisture: 22 },
          { name: "Orta", moisture: 28 },
          { name: "Güney", moisture: 31 },
        ]}
      />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 bg-gradient-to-t from-[#081c15]/80 via-[#081c15]/35 to-transparent px-4 pb-4 pt-16">
        <p className="text-sm font-semibold text-white">Antalya / Serik — örnek sera parseli</p>
        <p className="mt-0.5 text-xs text-white/75">
          OpenStreetMap · nem katmanı (simülasyon)
        </p>
      </div>
    </div>
  );
}
