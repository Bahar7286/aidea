"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/app/AppShell";
import { SchematicMap } from "@/components/app/SchematicMap";
import { api, Farm, ManagementZone, SensorReading } from "@/lib/api";

export default function ZonesPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [zones, setZones] = useState<ManagementZone[]>([]);
  const [reading, setReading] = useState<SensorReading | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    const [f, z, r] = await Promise.all([
      api.getFarm(farmId),
      api.listZones(farmId),
      api.listReadings(farmId).catch(() => []),
    ]);
    setFarm(f);
    setZones(z);
    setReading(r[0] || null);
    if (z[0] && selected == null) setSelected(z[0].id);
  }, [farmId, selected]);

  useEffect(() => {
    if (!farmId) return;
    refresh().catch((err) => setError(err.message));
  }, [farmId, refresh]);

  async function onCreate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
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
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Bölge eklenemedi.");
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
      </div>

      {error && <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>}

      <div className="grid gap-4 lg:grid-cols-2">
        <SchematicMap zones={mapZones.length ? mapZones : [{ name: "Bölge yok" }]} />

        <div className="space-y-4">
          <form onSubmit={onCreate} className="app-surface space-y-3 p-4">
            <h2 className="font-semibold">+ Bölge Ekle</h2>
            <p className="text-xs text-[var(--auth-muted)]">
              Tek sensör tüm araziyi temsil etmez. Bölgeleri toprak, eğim veya sulama
              hattına göre ayırın.
            </p>
            <input
              className="input"
              name="name"
              placeholder="Örn. Kuzey"
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
              <p className="text-sm text-[var(--auth-muted)]">Henüz bölge yok.</p>
            )}
          </div>

          {selectedZone && (
            <div className="app-surface space-y-2 p-4">
              <h3 className="font-semibold">{selectedZone.name} detayı</h3>
              <p className="text-sm text-[var(--auth-muted)]">
                Son nem (arazi geneli):{" "}
                {reading ? `%${reading.soil_moisture}` : "veri yok"}
              </p>
              <p className="text-xs text-[var(--auth-muted)]">
                Bölgeye sensör atama P1 cihaz ekranında tamamlanacak.
              </p>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
