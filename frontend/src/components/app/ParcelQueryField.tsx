"use client";

import { useEffect, useState } from "react";
import { api, GeoOption, ParcelQueryResult } from "@/lib/api";

export type ParcelFormValue = {
  latitude: string;
  longitude: string;
  area: string;
  location: string;
  parcel_ada: string;
  parcel_parsel: string;
  parcel_mahalle_id: number | null;
  geometry_geojson: string | null;
};

type Props = {
  value: ParcelFormValue;
  onChange: (next: ParcelFormValue) => void;
};

export function ParcelQueryField({ value, onChange }: Props) {
  const [provinces, setProvinces] = useState<GeoOption[]>([]);
  const [districts, setDistricts] = useState<GeoOption[]>([]);
  const [neighborhoods, setNeighborhoods] = useState<GeoOption[]>([]);
  const [ilId, setIlId] = useState("");
  const [ilceId, setIlceId] = useState("");
  const [mahalleId, setMahalleId] = useState(
    value.parcel_mahalle_id != null ? String(value.parcel_mahalle_id) : "",
  );
  const [ada, setAda] = useState(value.parcel_ada || "");
  const [parsel, setParsel] = useState(value.parcel_parsel || "");
  const [loadingList, setLoadingList] = useState(false);
  const [querying, setQuerying] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    setLoadingList(true);
    api
      .geoProvinces()
      .then(setProvinces)
      .catch((err) =>
        setError(
          err instanceof Error
            ? err.message
            : "İl listesi alınamadı. Konumu manuel girin.",
        ),
      )
      .finally(() => setLoadingList(false));
  }, []);

  useEffect(() => {
    if (!ilId) {
      setDistricts([]);
      return;
    }
    setLoadingList(true);
    setError("");
    api
      .geoDistricts(Number(ilId))
      .then(setDistricts)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "İlçeler yüklenemedi."),
      )
      .finally(() => setLoadingList(false));
  }, [ilId]);

  useEffect(() => {
    if (!ilceId) {
      setNeighborhoods([]);
      return;
    }
    setLoadingList(true);
    setError("");
    api
      .geoNeighborhoods(Number(ilceId))
      .then(setNeighborhoods)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Mahalleler yüklenemedi."),
      )
      .finally(() => setLoadingList(false));
  }, [ilceId]);

  function applyParcel(result: ParcelQueryResult) {
    const mahalleName =
      result.mahalle ||
      neighborhoods.find((n) => String(n.id) === mahalleId)?.name ||
      "";
    const ilName = provinces.find((p) => String(p.id) === ilId)?.name || "";
    const ilceName = districts.find((d) => String(d.id) === ilceId)?.name || "";
    const locParts = [ilName, ilceName, mahalleName].filter(Boolean);
    onChange({
      ...value,
      latitude: String(result.centroid.lat),
      longitude: String(result.centroid.lng),
      area:
        result.area_da != null
          ? String(result.area_da)
          : value.area,
      location: locParts.length ? locParts.join(" / ") : value.location,
      parcel_ada: result.ada,
      parcel_parsel: result.parsel,
      parcel_mahalle_id:
        typeof result.mahalle_id === "number"
          ? result.mahalle_id
          : Number(mahalleId) || null,
      geometry_geojson: JSON.stringify(result.geometry),
    });
    setMessage(
      result.area_da != null
        ? `Parsel alındı · ${result.area_da} da · merkez dolduruldu`
        : "Parsel alındı · alan TKGM’de yok, alanı elle girebilirsiniz",
    );
  }

  async function onQuery() {
    setError("");
    setMessage("");
    if (!mahalleId || !ada.trim() || !parsel.trim()) {
      setError("Mahalle, ada ve parsel gerekli.");
      return;
    }
    setQuerying(true);
    try {
      const result = await api.geoParcel({
        mahalle_id: Number(mahalleId),
        ada: ada.trim(),
        parsel: parsel.trim(),
      });
      applyParcel(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "TKGM servisine şu an ulaşılamıyor. Konumu manuel girin.",
      );
    } finally {
      setQuerying(false);
    }
  }

  function clearParcel() {
    setMessage("");
    setError("");
    onChange({
      ...value,
      parcel_ada: "",
      parcel_parsel: "",
      parcel_mahalle_id: null,
      geometry_geojson: null,
    });
  }

  return (
    <div className="space-y-3 rounded-xl border border-[var(--auth-border)] bg-[var(--auth-panel)]/40 p-4">
      <div>
        <p className="text-sm font-semibold">Parsel sorgula</p>
        <p className="mt-0.5 text-[11px] text-[var(--auth-muted)]">
          TKGM MEGSIS üzerinden isteğe bağlı konum yardımcısıdır; resmi ortaklık
          yoktur. Başarısız olursa lat / lng / alanı elle girin.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div>
          <label className="label" htmlFor="geo-il">
            İl
          </label>
          <select
            id="geo-il"
            className="input"
            value={ilId}
            disabled={loadingList}
            onChange={(e) => {
              setIlId(e.target.value);
              setIlceId("");
              setMahalleId("");
              setDistricts([]);
              setNeighborhoods([]);
            }}
          >
            <option value="">Seçiniz</option>
            {provinces.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="label" htmlFor="geo-ilce">
            İlçe
          </label>
          <select
            id="geo-ilce"
            className="input"
            value={ilceId}
            disabled={!ilId || loadingList}
            onChange={(e) => {
              setIlceId(e.target.value);
              setMahalleId("");
              setNeighborhoods([]);
            }}
          >
            <option value="">Seçiniz</option>
            {districts.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
        <div className="sm:col-span-2">
          <label className="label" htmlFor="geo-mahalle">
            Mahalle / köy
          </label>
          <select
            id="geo-mahalle"
            className="input"
            value={mahalleId}
            disabled={!ilceId || loadingList}
            onChange={(e) => setMahalleId(e.target.value)}
          >
            <option value="">Seçiniz</option>
            {neighborhoods.map((n) => (
              <option key={n.id} value={n.id}>
                {n.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="label" htmlFor="geo-ada">
            Ada
          </label>
          <input
            id="geo-ada"
            className="input"
            value={ada}
            onChange={(e) => setAda(e.target.value)}
            placeholder="örn. 101"
          />
        </div>
        <div>
          <label className="label" htmlFor="geo-parsel">
            Parsel
          </label>
          <input
            id="geo-parsel"
            className="input"
            value={parsel}
            onChange={(e) => setParsel(e.target.value)}
            placeholder="örn. 12"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className="btn btn-secondary text-sm"
          disabled={querying}
          onClick={onQuery}
        >
          {querying ? "Sorgulanıyor…" : "Parsel Sorgula"}
        </button>
        {(value.geometry_geojson || value.parcel_ada) && (
          <button
            type="button"
            className="btn btn-ghost text-sm"
            onClick={clearParcel}
          >
            Parseli temizle
          </button>
        )}
      </div>

      {message && (
        <p className="text-xs text-[var(--auth-forest)]">{message}</p>
      )}
      {error && <p className="text-xs text-[var(--risk-critical)]">{error}</p>}

      <div className="grid gap-3 border-t border-[var(--auth-border)] pt-3 sm:grid-cols-2">
        <div>
          <label className="label" htmlFor="manual-lat">
            Enlem (lat)
          </label>
          <input
            id="manual-lat"
            className="input"
            type="number"
            step="any"
            value={value.latitude}
            onChange={(e) => onChange({ ...value, latitude: e.target.value })}
            placeholder="36.9167"
          />
        </div>
        <div>
          <label className="label" htmlFor="manual-lng">
            Boylam (lng)
          </label>
          <input
            id="manual-lng"
            className="input"
            type="number"
            step="any"
            value={value.longitude}
            onChange={(e) => onChange({ ...value, longitude: e.target.value })}
            placeholder="31.1000"
          />
        </div>
      </div>
    </div>
  );
}
