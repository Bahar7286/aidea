"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/app/AppShell";
import { FarmMapPanel } from "@/components/app/FarmMapPanel";
import { api, Farm, ManagementZone, SensorReading } from "@/lib/api";

const QUICK_ZONES = ["Kuzey", "Orta", "Güney"];

export default function ZonesPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [zones, setZones] = useState<ManagementZone[]>([]);
  const [reading, setReading] = useState<SensorReading | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [editName, setEditName] = useState("");
  const [editNotes, setEditNotes] = useState("");
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    const [f, z, r] = await Promise.all([
      api.getFarm(farmId),
      api.listZones(farmId),
      api.listReadings(farmId).catch(() => []),
    ]);
    setFarm(f);
    setZones(z);
    setReading(r[0] || null);
    setSelected((prev) => {
      if (prev != null && z.some((row) => row.id === prev)) return prev;
      return z[0]?.id ?? null;
    });
  }, [farmId]);

  useEffect(() => {
    if (!farmId) return;
    refresh().catch((err) => setError(err.message));
  }, [farmId, refresh]);

  useEffect(() => {
    const z = zones.find((row) => row.id === selected);
    setEditName(z?.name || "");
    setEditNotes(z?.notes || "");
  }, [selected, zones]);

  async function onCreate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setOk("");
    const form = new FormData(e.currentTarget);
    const name = String(form.get("name") || "").trim();
    if (!name) return;
    try {
      await api.createZone({
        farm_id: farmId,
        name,
        notes: String(form.get("notes") || "") || undefined,
      });
      e.currentTarget.reset();
      setOk(`"${name}" eklendi`);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Bölge eklenemedi.");
    }
  }

  async function addQuick(name: string) {
    setError("");
    setOk("");
    if (zones.some((z) => z.name.toLowerCase() === name.toLowerCase())) {
      setError(`"${name}" zaten var.`);
      return;
    }
    try {
      await api.createZone({ farm_id: farmId, name });
      setOk(`"${name}" eklendi`);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Bölge eklenemedi.");
    }
  }

  async function onSaveEdit(e: FormEvent) {
    e.preventDefault();
    if (selected == null) return;
    setBusy(true);
    setError("");
    setOk("");
    try {
      await api.updateZone(selected, {
        name: editName.trim(),
        notes: editNotes.trim() || null,
      });
      setOk("Bölge güncellendi");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Güncellenemedi.");
    } finally {
      setBusy(false);
    }
  }

  async function onDelete() {
    if (selected == null) return;
    if (!confirm("Bu bölge silinsin mi?")) return;
    setBusy(true);
    setError("");
    try {
      await api.deleteZone(selected);
      setSelected(null);
      setOk("Bölge silindi");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Silinemedi.");
    } finally {
      setBusy(false);
    }
  }

  const selectedZone = zones.find((z) => z.id === selected) || zones[0];
  const mapZones = zones.map((z, i) => ({
    name: z.name,
    moisture:
      reading?.soil_moisture != null
        ? Math.max(10, Math.min(55, reading.soil_moisture + (i - 1) * 2.5))
        : null,
  }));

  return (
    <AppShell title="Arazi Bölgeleri" farmName={farm?.name}>
      <div className="mb-4 flex flex-wrap gap-2">
        <Link href={`/farms/${farmId}`} className="btn btn-ghost text-sm">
          ← Arazi detayı
        </Link>
        <Link href={`/farms/${farmId}/twin`} className="btn btn-ghost text-sm">
          Dijital ikiz
        </Link>
      </div>

      {error && <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>}
      {ok && <p className="mb-3 text-sm text-emerald-800">{ok}</p>}

      <div className="grid gap-4 lg:grid-cols-2">
        <FarmMapPanel
          farm={farm}
          zones={mapZones.length ? mapZones : [{ name: "Bölge yok", moisture: null }]}
          areaDa={farm?.area}
          sourceType={reading?.source_type || "simulation"}
          title="Bölge haritası"
          subtitle="OpenStreetMap · yönetim bölgeleri"
          heightClass="h-72 sm:h-96"
        />

        <div className="space-y-4">
          <form onSubmit={onCreate} className="app-surface space-y-3 p-4">
            <h2 className="font-semibold">+ Bölge ekle</h2>
            <p className="text-xs text-[var(--auth-muted)]">
              Tek sensör tüm araziyi temsil etmez. Kuzey / Orta / Güney ile başlayın veya
              kendi adınızı verin.
            </p>
            <div className="flex flex-wrap gap-2">
              {QUICK_ZONES.map((name) => (
                <button
                  key={name}
                  type="button"
                  className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-900 ring-1 ring-emerald-200"
                  onClick={() => addQuick(name)}
                >
                  {name}
                </button>
              ))}
            </div>
            <input
              className="input"
              name="name"
              placeholder="Örn. Batı sırt"
              required
            />
            <input className="input" name="notes" placeholder="Not (opsiyonel)" />
            <button className="btn btn-primary w-full">Bölge ekle</button>
          </form>

          <div className="space-y-2">
            {zones.map((z) => (
              <button
                key={z.id}
                type="button"
                onClick={() => setSelected(z.id)}
                className={`app-surface w-full p-4 text-left ${
                  selectedZone?.id === z.id ? "ring-2 ring-[var(--auth-forest)]" : ""
                }`}
              >
                <div className="flex items-center justify-between">
                  <p className="font-semibold">{z.name}</p>
                  <span className="text-xs text-[var(--auth-muted)]">#{z.id}</span>
                </div>
                {z.notes && (
                  <p className="mt-1 text-xs text-[var(--auth-muted)]">{z.notes}</p>
                )}
              </button>
            ))}
            {zones.length === 0 && (
              <p className="text-sm text-[var(--auth-muted)]">
                Henüz bölge yok. Kuzey / Orta / Güney ekleyin.
              </p>
            )}
          </div>

          {selectedZone && (
            <form onSubmit={onSaveEdit} className="app-surface space-y-3 p-4">
              <h3 className="font-semibold">Düzenle: {selectedZone.name}</h3>
              <input
                className="input"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                required
              />
              <input
                className="input"
                value={editNotes}
                onChange={(e) => setEditNotes(e.target.value)}
                placeholder="Not"
              />
              <p className="text-xs text-[var(--auth-muted)]">
                Son nem (arazi geneli):{" "}
                {reading ? `%${reading.soil_moisture}` : "veri yok"}
              </p>
              <div className="flex flex-wrap gap-2">
                <button className="btn btn-primary flex-1" disabled={busy}>
                  {busy ? "…" : "Kaydet"}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary text-[var(--risk-critical)]"
                  onClick={onDelete}
                  disabled={busy}
                >
                  Sil
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </AppShell>
  );
}
