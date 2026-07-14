"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import {
  api,
  CropHistory,
  CropHistoryList,
  CropSuggestions,
} from "@/lib/api";
import { CropTypeField } from "@/components/app/CropTypeField";

function toDateInput(iso: string | null | undefined): string {
  if (!iso) return "";
  return iso.slice(0, 10);
}

function fromDateInput(value: string): string {
  return new Date(`${value}T12:00:00`).toISOString();
}

const statusLabel: Record<string, string> = {
  growing: "Yetişiyor",
  harvested: "Hasat edildi",
};

type Props = { farmId: number };

export function CropHistoryPanel({ farmId }: Props) {
  const [list, setList] = useState<CropHistoryList | null>(null);
  const [suggestions, setSuggestions] = useState<CropSuggestions | null>(null);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [cropType, setCropType] = useState("marul");
  const [status, setStatus] = useState<"growing" | "harvested">("harvested");
  const [plantingDate, setPlantingDate] = useState("");
  const [harvestDate, setHarvestDate] = useState("");
  const [yieldAmount, setYieldAmount] = useState("");
  const [notes, setNotes] = useState("");

  const refresh = useCallback(async () => {
    const [hist, sug] = await Promise.all([
      api.listCropHistory(farmId),
      api.cropSuggestions(farmId),
    ]);
    setList(hist);
    setSuggestions(sug);
  }, [farmId]);

  useEffect(() => {
    if (!farmId) return;
    refresh().catch((err) => setError(err.message || "Yüklenemedi"));
  }, [farmId, refresh]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    if (!plantingDate) {
      setError("Ekim tarihi gerekli.");
      return;
    }
    if (status === "harvested" && !harvestDate) {
      setError("Hasat edilmiş sezon için hasat tarihi gerekli.");
      return;
    }
    setSaving(true);
    try {
      await api.createCropHistory(farmId, {
        crop_type: cropType,
        planting_date: fromDateInput(plantingDate),
        harvest_date: harvestDate ? fromDateInput(harvestDate) : null,
        status,
        yield_amount: yieldAmount ? Number(yieldAmount) : null,
        yield_unit: yieldAmount ? "kg/da" : null,
        notes: notes.trim() || null,
      });
      setShowForm(false);
      setNotes("");
      setYieldAmount("");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kayıt başarısız");
    } finally {
      setSaving(false);
    }
  }

  async function markHarvested(row: CropHistory) {
    const today = new Date().toISOString().slice(0, 10);
    const answered = window.prompt(
      "Hasat tarihi (YYYY-MM-DD):",
      today,
    );
    if (!answered) return;
    setSaving(true);
    setError("");
    try {
      await api.updateCropHistory(row.id, {
        status: "harvested",
        harvest_date: fromDateInput(answered),
      });
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Güncelleme başarısız");
    } finally {
      setSaving(false);
    }
  }

  async function removeRow(id: number) {
    if (!window.confirm("Bu sezon kaydı silinsin mi?")) return;
    setSaving(true);
    try {
      await api.deleteCropHistory(id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Silinemedi");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="grid gap-6 lg:grid-cols-2">
      <div className="card space-y-3">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div>
            <h2 className="font-semibold">Ürün geçmişi</h2>
            <p className="text-xs text-muted">
              Çiftlik kaydı · <strong>source_type: manual</strong> · IoT değil
            </p>
          </div>
          <button
            type="button"
            className="btn btn-secondary text-sm"
            onClick={() => setShowForm((v) => !v)}
          >
            {showForm ? "Formu kapat" : "Sezon ekle"}
          </button>
        </div>

        {list?.current_crop && (
          <p className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
            Şu an: <strong>{list.current_crop.crop_type}</strong>
            {list.current_crop.days_since_planting != null && (
              <> · ekimden {list.current_crop.days_since_planting} gün</>
            )}
          </p>
        )}
        {list?.days_since_harvest != null && (
          <p className="text-sm text-muted">
            Son hasattan bu yana{" "}
            <strong>{list.days_since_harvest} gün</strong>
            {list.last_harvested && <> ({list.last_harvested.crop_type})</>}
          </p>
        )}
        {list?.soil_condition_summary && (
          <p className="text-xs text-muted">
            Toprak özeti: {list.soil_condition_summary}
          </p>
        )}

        {error && <p className="text-sm text-red-600">{error}</p>}

        {showForm && (
          <form className="space-y-3 rounded-xl border border-border p-3" onSubmit={onSubmit}>
            <div>
              <label className="label">Ürün</label>
              <CropTypeField value={cropType} onChange={setCropType} required />
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <label className="label" htmlFor="ch_status">
                  Durum
                </label>
                <select
                  id="ch_status"
                  className="input"
                  value={status}
                  onChange={(e) =>
                    setStatus(e.target.value as "growing" | "harvested")
                  }
                >
                  <option value="harvested">Hasat edildi</option>
                  <option value="growing">Yetişiyor</option>
                </select>
              </div>
              <div>
                <label className="label" htmlFor="ch_yield">
                  Verim (kg/da, isteğe bağlı)
                </label>
                <input
                  id="ch_yield"
                  className="input"
                  type="number"
                  min={0}
                  step="0.1"
                  value={yieldAmount}
                  onChange={(e) => setYieldAmount(e.target.value)}
                />
              </div>
              <div>
                <label className="label" htmlFor="ch_plant">
                  Ekim tarihi *
                </label>
                <input
                  id="ch_plant"
                  className="input"
                  type="date"
                  required
                  value={plantingDate}
                  onChange={(e) => setPlantingDate(e.target.value)}
                />
              </div>
              <div>
                <label className="label" htmlFor="ch_harvest">
                  Hasat tarihi {status === "harvested" ? "*" : ""}
                </label>
                <input
                  id="ch_harvest"
                  className="input"
                  type="date"
                  required={status === "harvested"}
                  value={harvestDate}
                  onChange={(e) => setHarvestDate(e.target.value)}
                />
              </div>
            </div>
            <div>
              <label className="label" htmlFor="ch_notes">
                Not
              </label>
              <input
                id="ch_notes"
                className="input"
                value={notes}
                maxLength={500}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Örn. sera kuzey hücreleri"
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? "Kaydediliyor…" : "Kaydet"}
            </button>
          </form>
        )}

        {!list || list.items.length === 0 ? (
          <p className="text-sm text-muted">Henüz sezon kaydı yok.</p>
        ) : (
          <ul className="space-y-2 text-sm">
            {list.items.map((row) => (
              <li
                key={row.id}
                className="flex flex-wrap items-start justify-between gap-2 border-b border-border pb-2"
              >
                <div>
                  <p className="font-medium">
                    {row.crop_type}{" "}
                    <span className="text-xs font-normal text-muted">
                      · {statusLabel[row.status] || row.status}
                      {row.family ? ` · ${row.family}` : ""}
                    </span>
                  </p>
                  <p className="text-xs text-muted">
                    Ekim {toDateInput(row.planting_date)}
                    {row.harvest_date && <> · Hasat {toDateInput(row.harvest_date)}</>}
                    {row.days_since_harvest != null && (
                      <> · {row.days_since_harvest} gündür hasatlı</>
                    )}
                    {row.yield_amount != null && (
                      <> · {row.yield_amount} {row.yield_unit || "kg/da"}</>
                    )}
                  </p>
                  {row.notes && (
                    <p className="text-xs text-muted">{row.notes}</p>
                  )}
                </div>
                <div className="flex gap-1">
                  {row.status === "growing" && (
                    <button
                      type="button"
                      className="btn btn-ghost text-xs"
                      disabled={saving}
                      onClick={() => markHarvested(row)}
                    >
                      Hasat et
                    </button>
                  )}
                  <button
                    type="button"
                    className="btn btn-ghost text-xs text-red-700"
                    disabled={saving}
                    onClick={() => removeRow(row.id)}
                  >
                    Sil
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="card space-y-3">
        <div>
          <h2 className="font-semibold">Şimdi ekilebilir öneriler</h2>
          <p className="text-xs text-muted">
            Kural tabanlı rotasyon · gübre/ilaç reçetesi yok
            {suggestions?.llm_enriched ? " · LLM açıklama zenginleştirmesi" : ""}
          </p>
        </div>
        {suggestions?.explanation && (
          <p className="rounded-lg border border-border bg-[var(--background)] p-3 text-sm">
            {suggestions.explanation}
          </p>
        )}
        {suggestions && suggestions.suggestions.length > 0 ? (
          <ul className="space-y-2">
            {suggestions.suggestions.map((s) => (
              <li
                key={s.crop_type}
                className={`rounded-lg border px-3 py-2 text-sm ${
                  s.suitable_now
                    ? "border-emerald-200 bg-emerald-50/60"
                    : "border-border opacity-80"
                }`}
              >
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <span className="font-medium">
                    {s.label_tr}{" "}
                    <span className="text-xs font-normal text-muted">
                      ({s.crop_type})
                    </span>
                  </span>
                  <span className="text-xs text-muted">
                    skor {s.score}
                    {s.suitable_now ? " · uygun" : " · şimdilik değil"}
                  </span>
                </div>
                <ul className="mt-1 list-disc pl-4 text-xs text-muted">
                  {s.reasons.slice(0, 3).map((r) => (
                    <li key={r}>{r}</li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted">Öneri yükleniyor veya veri yok.</p>
        )}
      </div>
    </section>
  );
}
