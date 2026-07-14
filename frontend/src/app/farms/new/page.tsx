"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/app/AppShell";
import { CropTypeField } from "@/components/app/CropTypeField";
import {
  FarmMaterialsField,
  MaterialSelection,
} from "@/components/app/FarmMaterialsField";
import { setSelectedFarmId } from "@/components/app/FarmSelector";
import { api } from "@/lib/api";
import { SchematicMap } from "@/components/app/SchematicMap";
import { Radio } from "lucide-react";

const STEPS = ["Temel Bilgi", "Konum", "Bölge / Malzeme", "Özet"];

export default function NewFarmPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: "Domates Serası",
    location: "",
    area: "2",
    soil_type: "tınlı",
    irrigation_type: "damla",
    crop_type: "domates",
    growth_stage: "çiçeklenme",
    zone_hint: "3",
  });
  const [materials, setMaterials] = useState<MaterialSelection[]>([]);

  function update(key: string, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (step < 3) {
      setStep((s) => s + 1);
      return;
    }
    setLoading(true);
    setError("");
    try {
      const farm = await api.createFarm({
        name: form.name,
        location: form.location || null,
        area: form.area ? Number(form.area) : null,
        soil_type: form.soil_type || null,
        irrigation_type: form.irrigation_type || null,
        crop_type: form.crop_type || null,
        growth_stage: form.growth_stage || null,
        materials: materials.length
          ? materials.map((m) => ({
              material_id: m.material_id,
              notes: m.notes || null,
              frequency: m.frequency || null,
              last_applied_at: m.last_applied_at || null,
              is_last_fertilizer: !!m.is_last_fertilizer,
              is_last_pesticide: !!m.is_last_pesticide,
            }))
          : undefined,
      });
      const n = Math.min(5, Math.max(0, Number(form.zone_hint) || 0));
      const names = ["Kuzey", "Orta", "Güney", "Doğu", "Batı"];
      for (let i = 0; i < n; i++) {
        await api.createZone({ farm_id: farm.id, name: names[i] || `Bölge ${i + 1}` }).catch(() => undefined);
      }
      setSelectedFarmId(farm.id);
      router.push(`/farms/${farm.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Arazi oluşturulamadı.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell title="Yeni Arazi Ekle">
      <ol className="mb-6 grid grid-cols-4 gap-2">
        {STEPS.map((label, i) => (
          <li key={label} className="text-center">
            <span
              className={`mx-auto flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${
                i <= step
                  ? "bg-[var(--auth-forest)] text-white"
                  : "bg-[var(--auth-border)] text-[var(--auth-muted)]"
              }`}
            >
              {i + 1}
            </span>
            <span className="mt-1 hidden text-[10px] text-[var(--auth-muted)] sm:block">
              {label}
            </span>
          </li>
        ))}
      </ol>

      <form onSubmit={onSubmit} className="grid gap-6 lg:grid-cols-2">
        <div className="app-surface space-y-3 p-5">
          {step === 0 && (
            <>
              <h2 className="font-semibold">Temel bilgiler</h2>
              <div>
                <label className="label" htmlFor="name">
                  Arazi adı *
                </label>
                <input
                  className="input"
                  id="name"
                  required
                  value={form.name}
                  onChange={(e) => update("name", e.target.value)}
                />
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="label" htmlFor="crop_type">
                    Ürün türü
                  </label>
                  <CropTypeField
                    id="crop_type"
                    value={form.crop_type}
                    onChange={(v) => update("crop_type", v)}
                  />
                </div>
                <div>
                  <label className="label" htmlFor="soil_type">
                    Toprak türü
                  </label>
                  <select
                    className="input"
                    id="soil_type"
                    value={form.soil_type}
                    onChange={(e) => update("soil_type", e.target.value)}
                  >
                    <option value="tınlı">Tınlı</option>
                    <option value="kumlu">Kumlu</option>
                    <option value="killi">Killi</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="label" htmlFor="irrigation_type">
                  Sulama sistemi
                </label>
                <select
                  className="input"
                  id="irrigation_type"
                  value={form.irrigation_type}
                  onChange={(e) => update("irrigation_type", e.target.value)}
                >
                  <option value="damla">Damla</option>
                  <option value="yagmurlama">Yağmurlama</option>
                  <option value="salma">Salma</option>
                </select>
              </div>
              <div>
                <label className="label" htmlFor="area">
                  Alan (da)
                </label>
                <input
                  className="input"
                  id="area"
                  type="number"
                  step="0.1"
                  value={form.area}
                  onChange={(e) => update("area", e.target.value)}
                />
              </div>
            </>
          )}

          {step === 1 && (
            <>
              <h2 className="font-semibold">Konum</h2>
              <div>
                <label className="label" htmlFor="location">
                  İl / ilçe veya açıklama
                </label>
                <input
                  className="input"
                  id="location"
                  placeholder="Antalya / Serik"
                  value={form.location}
                  onChange={(e) => update("location", e.target.value)}
                />
              </div>
              <p className="text-xs text-[var(--auth-muted)]">
                MVP’de harita çizimi şematiktir; sınır poligonu P2 (Leaflet).
              </p>
              <div>
                <label className="label" htmlFor="growth_stage">
                  Gelişim dönemi
                </label>
                <input
                  className="input"
                  id="growth_stage"
                  value={form.growth_stage}
                  onChange={(e) => update("growth_stage", e.target.value)}
                />
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <h2 className="font-semibold">Bölge ve malzeme profili</h2>
              <p className="text-sm text-[var(--auth-muted)]">
                Tek sensör tüm araziyi temsil etmez. İsterseniz başlangıç bölgeleri
                oluşturun. Gübre/ilaç seçimi isteğe bağlıdır — reçete değil, bağlamdır.
              </p>
              <div>
                <label className="label" htmlFor="zone_hint">
                  Başlangıç bölge sayısı
                </label>
                <select
                  className="input"
                  id="zone_hint"
                  value={form.zone_hint}
                  onChange={(e) => update("zone_hint", e.target.value)}
                >
                  <option value="0">Şimdilik yok</option>
                  <option value="1">1</option>
                  <option value="2">2</option>
                  <option value="3">3</option>
                </select>
              </div>
              <FarmMaterialsField value={materials} onChange={setMaterials} />
            </>
          )}

          {step === 3 && (
            <>
              <h2 className="font-semibold">Özet</h2>
              <ul className="space-y-1 text-sm text-[var(--auth-muted)]">
                <li>
                  <strong className="text-[var(--auth-ink)]">{form.name}</strong>
                </li>
                <li>
                  {form.crop_type} · {form.soil_type} · {form.irrigation_type}
                </li>
                <li>
                  {form.location || "Konum yok"} · {form.area || "—"} da
                </li>
                <li>Başlangıç bölge: {form.zone_hint}</li>
                <li>Malzeme sınıfı: {materials.length || "seçilmedi"}</li>
              </ul>
            </>
          )}

          {error && <p className="text-sm text-[var(--risk-critical)]">{error}</p>}

          <div className="flex flex-wrap gap-2 pt-2">
            <Link href="/farms" className="btn btn-ghost">
              İptal
            </Link>
            {step > 0 && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setStep((s) => s - 1)}
              >
                Geri
              </button>
            )}
            <button className="btn btn-primary flex-1" disabled={loading}>
              {step < 3
                ? "İleri"
                : loading
                  ? "Kaydediliyor..."
                  : "Araziyi Oluştur"}
            </button>
          </div>
        </div>

        <div className="app-surface overflow-hidden">
          <div className="flex items-center justify-between border-b border-[var(--auth-border)] px-4 py-2.5 text-sm font-semibold">
            <span className="inline-flex items-center gap-2">
              <Radio className="h-4 w-4 text-emerald-700" aria-hidden />
              Şematik önizleme
            </span>
            <span className="text-[10px] font-medium text-[var(--auth-muted)]">
              Alan değişince ölçeklenir
            </span>
          </div>
          <div className="p-3">
            <SchematicMap
              areaDa={form.area ? Number(form.area) : 2}
              zones={[
                { name: "Kuzey", moisture: 32 },
                { name: "Orta", moisture: 28 },
                { name: "Güney", moisture: 24 },
              ]}
            />
          </div>
        </div>
      </form>
    </AppShell>
  );
}
