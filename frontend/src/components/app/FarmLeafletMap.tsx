"use client";

import { useEffect, useMemo } from "react";
import {
  CircleMarker,
  MapContainer,
  Polygon,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

export type MapZone = {
  name: string;
  moisture?: number | null;
};

type FarmLeafletMapProps = {
  latitude: number;
  longitude: number;
  zones?: MapZone[];
  areaDa?: number | null;
  heightClass?: string;
  interactive?: boolean;
  className?: string;
};

function moistureColor(m: number | null | undefined) {
  if (m == null) return "#94a3b8";
  if (m < 25) return "#fb923c";
  if (m < 32) return "#fbbf24";
  return "#22c55e";
}

/** Approximate zone polygons around farm center; size scales with area (da). */
function zonePolygons(
  lat: number,
  lng: number,
  zones: MapZone[],
  areaDa: number,
): Array<{ zone: MapZone; positions: [number, number][] }> {
  const n = Math.max(1, zones.length);
  // ~0.001 deg ≈ 111 m; scale with sqrt(area)
  const span = Math.min(0.018, Math.max(0.004, Math.sqrt(areaDa / 2) * 0.006));
  const halfH = span * 0.55;
  const slice = (span * 2) / n;

  return zones.map((zone, i) => {
    const x0 = -span + i * slice;
    const x1 = x0 + slice * 0.92;
    const wobble = (i % 2 === 0 ? 1 : -1) * span * 0.08;
    const positions: [number, number][] = [
      [lat + halfH + wobble, lng + x0],
      [lat + halfH - wobble * 0.5, lng + x1],
      [lat - halfH - wobble, lng + x1 + wobble * 0.3],
      [lat - halfH + wobble * 0.4, lng + x0 - wobble * 0.2],
    ];
    return { zone, positions };
  });
}

function Recenter({ lat, lng }: { lat: number; lng: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView([lat, lng]);
  }, [lat, lng, map]);
  return null;
}

export function FarmLeafletMap({
  latitude,
  longitude,
  zones = [],
  areaDa,
  heightClass = "h-64 sm:h-80",
  interactive = true,
  className = "",
}: FarmLeafletMapProps) {
  const area = Math.max(0.5, areaDa ?? 2);
  const polys = useMemo(() => {
    const displayZones =
      zones.length > 0
        ? zones.slice(0, 5)
        : [
            { name: "Bölge A", moisture: null },
            { name: "Bölge B", moisture: null },
            { name: "Bölge C", moisture: null },
          ];
    return zonePolygons(latitude, longitude, displayZones, area);
  }, [latitude, longitude, zones, area]);

  const zoom = area >= 8 ? 13 : area >= 3 ? 14 : 15;

  useEffect(() => {
    // Fix default marker icons when bundling with Next
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    delete (L.Icon.Default.prototype as any)._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
      iconUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
      shadowUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
    });
  }, []);

  return (
    <div className={`overflow-hidden ${heightClass} ${className}`}>
      <MapContainer
        center={[latitude, longitude]}
        zoom={zoom}
        className="h-full w-full"
        scrollWheelZoom={interactive}
        dragging={interactive}
        doubleClickZoom={interactive}
        zoomControl={interactive}
        attributionControl
      >
        <Recenter lat={latitude} lng={longitude} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {polys.map(({ zone, positions }) => (
          <Polygon
            key={zone.name}
            positions={positions}
            pathOptions={{
              color: "#ffffff",
              weight: 1.5,
              fillColor: moistureColor(zone.moisture),
              fillOpacity: 0.72,
            }}
          >
            <Popup>
              <strong>{zone.name}</strong>
              <br />
              Nem: {zone.moisture != null ? `%${zone.moisture}` : "—"}
            </Popup>
          </Polygon>
        ))}
        <CircleMarker
          center={[latitude, longitude]}
          radius={7}
          pathOptions={{ color: "#ecfccb", fillColor: "#65a30d", fillOpacity: 1, weight: 2 }}
        >
          <Popup>Arazi merkezi</Popup>
        </CircleMarker>
      </MapContainer>
    </div>
  );
}
