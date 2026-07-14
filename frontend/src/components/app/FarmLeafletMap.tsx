"use client";

import { useEffect, useMemo, useState } from "react";
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
  /** When set, draw real parcel boundary instead of schematic moisture zones. */
  geometryGeoJson?: string | null;
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

function parseParcelPositions(
  geometryGeoJson?: string | null,
): [number, number][] | null {
  if (!geometryGeoJson) return null;
  try {
    const g = JSON.parse(geometryGeoJson) as {
      type?: string;
      coordinates?: unknown;
      geometry?: { type?: string; coordinates?: unknown };
    };
    const geom = g.geometry || g;
    const type = geom.type;
    const coords = geom.coordinates as number[][][] | number[][][][] | undefined;
    if (!coords) return null;
    let ring: number[][] | undefined;
    if (type === "Polygon") {
      ring = (coords as number[][][])[0];
    } else if (type === "MultiPolygon") {
      ring = (coords as number[][][][])[0]?.[0];
    }
    if (!ring?.length) return null;
    return ring.map((c) => [c[1], c[0]] as [number, number]);
  } catch {
    return null;
  }
}

function Recenter({ lat, lng, zoom }: { lat: number; lng: number; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView([lat, lng], zoom);
    const t = window.setTimeout(() => map.invalidateSize(), 120);
    return () => window.clearTimeout(t);
  }, [lat, lng, zoom, map]);
  return null;
}

function FitParcel({ positions }: { positions: [number, number][] }) {
  const map = useMap();
  useEffect(() => {
    if (positions.length < 2) return;
    const bounds = L.latLngBounds(positions);
    map.fitBounds(bounds, { padding: [28, 28], maxZoom: 17 });
  }, [map, positions]);
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
  geometryGeoJson,
}: FarmLeafletMapProps) {
  const [ready, setReady] = useState(false);
  const area = Math.max(0.5, areaDa ?? 2);
  const lat = Number.isFinite(latitude) ? latitude : 39.0;
  const lng = Number.isFinite(longitude) ? longitude : 35.0;
  const parcelPositions = useMemo(
    () => parseParcelPositions(geometryGeoJson),
    [geometryGeoJson],
  );

  const polys = useMemo(() => {
    if (parcelPositions) return [];
    const displayZones =
      zones.length > 0
        ? zones.slice(0, 5)
        : [
            { name: "Bölge A", moisture: null },
            { name: "Bölge B", moisture: null },
            { name: "Bölge C", moisture: null },
          ];
    return zonePolygons(lat, lng, displayZones, area);
  }, [lat, lng, zones, area, parcelPositions]);

  const zoom = area >= 8 ? 13 : area >= 3 ? 14 : 15;

  useEffect(() => {
    setReady(true);
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

  if (!ready) {
    return (
      <div
        className={`flex items-center justify-center bg-emerald-950/10 text-sm text-[var(--auth-muted)] ${heightClass} ${className}`}
      >
        Harita hazırlanıyor…
      </div>
    );
  }

  return (
    <div className={`relative overflow-hidden bg-slate-100 ${heightClass} ${className}`}>
      <MapContainer
        key={`${lat.toFixed(4)}-${lng.toFixed(4)}-${parcelPositions ? "p" : "z"}`}
        center={[lat, lng]}
        zoom={zoom}
        className="h-full w-full"
        style={{ height: "100%", width: "100%", minHeight: 240 }}
        scrollWheelZoom={interactive}
        dragging={interactive}
        doubleClickZoom={interactive}
        zoomControl={interactive}
        attributionControl
      >
        {parcelPositions ? (
          <FitParcel positions={parcelPositions} />
        ) : (
          <Recenter lat={lat} lng={lng} zoom={zoom} />
        )}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />
        {parcelPositions && (
          <Polygon
            positions={parcelPositions}
            pathOptions={{
              color: "#166534",
              weight: 2.5,
              fillColor: "#4ade80",
              fillOpacity: 0.35,
            }}
          >
            <Popup>Kadastro parseli (TKGM MEGSIS · resmi ortaklık yok)</Popup>
          </Polygon>
        )}
        {polys.map(({ zone, positions }) => (
          <Polygon
            key={zone.name}
            positions={positions}
            pathOptions={{
              color: "#ffffff",
              weight: 1.5,
              fillColor: moistureColor(zone.moisture),
              fillOpacity: 0.55,
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
          center={[lat, lng]}
          radius={7}
          pathOptions={{
            color: "#ecfccb",
            fillColor: "#65a30d",
            fillOpacity: 1,
            weight: 2,
          }}
        >
          <Popup>Arazi merkezi</Popup>
        </CircleMarker>
      </MapContainer>
    </div>
  );
}
