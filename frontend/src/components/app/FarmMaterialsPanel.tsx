"use client";

import { useEffect, useState } from "react";
import {
  FarmMaterialsField,
  MaterialSelection,
} from "@/components/app/FarmMaterialsField";
import { api, Farm } from "@/lib/api";

type Props = {
  farmId: number;
  initialUses?: Farm["material_uses"];
  onSaved?: (farm: Farm) => void;
};

export function FarmMaterialsPanel({ farmId, initialUses, onSaved }: Props) {
  const [materials, setMaterials] = useState<MaterialSelection[]>([]);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setMaterials(
      (initialUses || []).map((u) => ({
        material_id: u.material_id,
        notes: u.notes,
        frequency: u.frequency,
        last_applied_at: u.last_applied_at,
        is_last_fertilizer: !!u.is_last_fertilizer,
        is_last_pesticide: !!u.is_last_pesticide,
      })),
    );
  }, [initialUses]);

  async function save() {
    setBusy(true);
    setError("");
    setMsg("");
    try {
      await api.syncFarmMaterials(
        farmId,
        materials.map((m) => ({
          material_id: m.material_id,
          notes: m.notes || null,
          frequency: m.frequency || null,
          last_applied_at: m.last_applied_at || null,
          is_last_fertilizer: !!m.is_last_fertilizer,
          is_last_pesticide: !!m.is_last_pesticide,
        })),
      );
      const farm = await api.getFarm(farmId);
      onSaved?.(farm);
      setMsg("Malzeme profili kaydedildi (reçete değil — kullanım kaydı).");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kaydedilemedi");
    } finally {
      setBusy(false);
    }
  }

  const lastFertUse = (initialUses || []).find((u) => u.is_last_fertilizer);
  const lastPestUse = (initialUses || []).find((u) => u.is_last_pesticide);

  return (
    <div className="app-surface space-y-3 p-4">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h2 className="font-semibold">Gübre / ilaç kullanım kaydı</h2>
          <p className="text-xs text-[var(--auth-muted)]">
            Katalogdan seçim · son kullanılan sınıf AI sulama/EC bağlamında
            kullanılır · doz reçetesi yok
          </p>
        </div>
        <button
          type="button"
          className="btn btn-primary min-h-11 text-sm"
          disabled={busy}
          onClick={save}
        >
          {busy ? "Kaydediliyor…" : "Kaydet"}
        </button>
      </div>
      {(lastFertUse || lastPestUse) && (
        <ul className="space-y-1 text-xs text-[var(--auth-muted)]">
          {lastFertUse && (
            <li>
              Son gübre:{" "}
              <strong className="text-[var(--auth-ink)]">
                {lastFertUse.material?.name_tr || `#${lastFertUse.material_id}`}
              </strong>
              {lastFertUse.last_applied_at
                ? ` · ${String(lastFertUse.last_applied_at).slice(0, 10)}`
                : ""}
            </li>
          )}
          {lastPestUse && (
            <li>
              Son ilaç:{" "}
              <strong className="text-[var(--auth-ink)]">
                {lastPestUse.material?.name_tr || `#${lastPestUse.material_id}`}
              </strong>
              {lastPestUse.last_applied_at
                ? ` · ${String(lastPestUse.last_applied_at).slice(0, 10)}`
                : ""}
            </li>
          )}
        </ul>
      )}
      {error && <p className="text-sm text-[var(--risk-critical)]">{error}</p>}
      {msg && <p className="text-sm text-[var(--auth-forest)]">{msg}</p>}
      <FarmMaterialsField
        value={materials}
        onChange={setMaterials}
        alwaysOpen
        title="Kullanılan sınıflar ve son uygulama"
      />
    </div>
  );
}
