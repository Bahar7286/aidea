"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { AppShell } from "@/components/app/AppShell";
import { CropTypeField } from "@/components/app/CropTypeField";
import {
  FarmMaterialsField,
  MaterialSelection,
} from "@/components/app/FarmMaterialsField";
import { FarmMapPanel } from "@/components/app/FarmMapPanel";
import {
  ParcelFormValue,
  ParcelQueryField,
} from "@/components/app/ParcelQueryField";
import { setSelectedFarmId } from "@/components/app/FarmSelector";
import { api, Farm } from "@/lib/api";

export default function EditFarmPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const router = useRouter();
  const [farm, setFarm] = useState<Farm | null>(null);
  const [cropType, setCropType] = useState("domates");
  const [parcel, setParcel] = useState<ParcelFormValue>({
    latitude: "",
    longitude: "",
    area: "",
    location: "",
    parcel_ada: "",
    parcel_parsel: "",
    parcel_mahalle_id: null,
    geometry_geojson: null,
  });
  const [materials, setMaterials] = useState<MaterialSelection[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!farmId) return;
    setSelectedFarmId(farmId);
    api
      .getFarm(farmId)
      .then((f) => {
        setFarm(f);
        setCropType(f.crops[0]?.crop_type || "domates");
        setParcel({
          latitude: f.latitude != null ? String(f.latitude) : "",
          longitude: f.longitude != null ? String(f.longitude) : "",
          area: f.area != null ? String(f.area) : "",
          location: f.location || "",
          parcel_ada: f.parcel_ada || "",
          parcel_parsel: f.parcel_parsel || "",
          parcel_mahalle_id: f.parcel_mahalle_id ?? null,
          geometry_geojson: f.geometry_geojson ?? null,
        });
        setMaterials(
          (f.material_uses || []).map((u) => ({
            material_id: u.material_id,
            notes: u.notes,
            frequency: u.frequency,
            last_applied_at: u.last_applied_at,
            is_last_fertilizer: !!u.is_last_fertilizer,
            is_last_pesticide: !!u.is_last_pesticide,
          }))
        );
      })
      .catch((err) => setError(err.message));
  }, [farmId]);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!farm) return;
    setLoading(true);
    setError("");
    const form = new FormData(e.currentTarget);
    try {
      const lat = parcel.latitude ? Number(parcel.latitude) : null;
      const lng = parcel.longitude ? Number(parcel.longitude) : null;
      const updated = await api.updateFarm(farmId, {
        name: String(form.get("name")),
        location: parcel.location || null,
        latitude: lat != null && Number.isFinite(lat) ? lat : null,
        longitude: lng != null && Number.isFinite(lng) ? lng : null,
        area: parcel.area ? Number(parcel.area) : null,
        soil_type: String(form.get("soil_type") || "") || null,
        irrigation_type: String(form.get("irrigation_type") || "") || null,
        is_active: form.get("is_active") === "on",
        crop_type: cropType || null,
        growth_stage: String(form.get("growth_stage") || "") || null,
        parcel_ada: parcel.parcel_ada || null,
        parcel_parsel: parcel.parcel_parsel || null,
        parcel_mahalle_id: parcel.parcel_mahalle_id,
        geometry_geojson: parcel.geometry_geojson,
        materials: materials.map((m) => ({
          material_id: m.material_id,
          notes: m.notes || null,
          frequency: m.frequency || null,
          last_applied_at: m.last_applied_at || null,
          is_last_fertilizer: !!m.is_last_fertilizer,
          is_last_pesticide: !!m.is_last_pesticide,
        })),
      });
      setFarm(updated);
      router.push(`/farms/${farmId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kaydedilemedi.");
    } finally {
      setLoading(false);
    }
  }

  async function onDelete() {
    if (!confirm("Bu arazi silinsin mi?")) return;
    await api.deleteFarm(farmId);
    router.push("/farms");
  }

  if (!farm) {
    return (
      <AppShell title="Arazi Düzenle">
        <p className="text-sm text-[var(--auth-muted)]">{error || "Yükleniyor..."}</p>
      </AppShell>
    );
  }

  const previewFarm = {
    ...farm,
    area: parcel.area ? Number(parcel.area) : farm.area,
    latitude: parcel.latitude ? Number(parcel.latitude) : farm.latitude,
    longitude: parcel.longitude ? Number(parcel.longitude) : farm.longitude,
    location: parcel.location || farm.location,
    geometry_geojson: parcel.geometry_geojson,
  };

  return (
    <AppShell title="Arazi Düzenle" farmName={farm.name}>
      <form onSubmit={onSubmit} className="grid gap-6 xl:grid-cols-[1fr_360px]">
        <div className="space-y-4">
          <div className="app-surface flex items-center justify-between p-4">
            <div>
              <p className="font-semibold">{farm.name}</p>
              <p className="text-xs text-[var(--auth-muted)]">Aktif / pasif durumu</p>
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                name="is_active"
                defaultChecked={farm.is_active !== false}
                className="size-4 accent-[var(--auth-forest)]"
              />
              Aktif
            </label>
          </div>

          <div className="app-surface grid gap-3 p-5 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="label" htmlFor="name">
                Arazi adı
              </label>
              <input
                className="input"
                id="name"
                name="name"
                defaultValue={farm.name}
                required
              />
            </div>
            <div className="sm:col-span-2">
              <label className="label" htmlFor="location">
                Konum
              </label>
              <input
                className="input"
                id="location"
                name="location"
                value={parcel.location}
                onChange={(e) =>
                  setParcel((p) => ({ ...p, location: e.target.value }))
                }
              />
            </div>
            <div>
              <label className="label" htmlFor="area">
                Alan (da)
              </label>
              <input
                className="input"
                id="area"
                name="area"
                type="number"
                step="0.1"
                value={parcel.area}
                onChange={(e) =>
                  setParcel((p) => ({ ...p, area: e.target.value }))
                }
              />
            </div>
            <div>
              <label className="label" htmlFor="soil_type">
                Toprak türü
              </label>
              <input
                className="input"
                id="soil_type"
                name="soil_type"
                defaultValue={farm.soil_type || ""}
              />
            </div>
            <div>
              <label className="label" htmlFor="irrigation_type">
                Sulama
              </label>
              <input
                className="input"
                id="irrigation_type"
                name="irrigation_type"
                defaultValue={farm.irrigation_type || ""}
              />
            </div>
            <div>
              <label className="label" htmlFor="crop_type">
                Ürün
              </label>
              <CropTypeField
                id="crop_type"
                value={cropType}
                onChange={setCropType}
              />
            </div>
            <div className="sm:col-span-2">
              <label className="label" htmlFor="growth_stage">
                Gelişim dönemi
              </label>
              <input
                className="input"
                id="growth_stage"
                name="growth_stage"
                defaultValue={farm.crops[0]?.growth_stage || ""}
              />
            </div>
            <div className="sm:col-span-2">
              <ParcelQueryField value={parcel} onChange={setParcel} />
            </div>
            <div className="sm:col-span-2">
              <FarmMaterialsField value={materials} onChange={setMaterials} />
            </div>
          </div>

          {error && <p className="text-sm text-[var(--risk-critical)]">{error}</p>}

          <div className="flex flex-wrap gap-2">
            <Link href={`/farms/${farmId}`} className="btn btn-ghost">
              İptal
            </Link>
            <button
              type="button"
              className="btn btn-secondary text-[var(--risk-critical)]"
              onClick={onDelete}
            >
              Sil
            </button>
            <button className="btn btn-primary flex-1" disabled={loading}>
              {loading ? "Kaydediliyor..." : "Değişiklikleri Kaydet"}
            </button>
          </div>
        </div>

        <FarmMapPanel
          farm={previewFarm}
          zones={[
            { name: "Kuzey", moisture: 30 },
            { name: "Orta", moisture: 27 },
            { name: "Güney", moisture: 23 },
          ]}
          areaDa={parcel.area ? Number(parcel.area) : farm.area}
          sourceType="simulation"
          title="Arazi önizleme"
          heightClass="h-72"
          interactive={false}
        />
      </form>
    </AppShell>
  );
}
