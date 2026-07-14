"use client";

import { useEffect, useState } from "react";
import { api, AgroMaterial } from "@/lib/api";

export type MaterialSelection = {
  material_id: number;
  notes?: string | null;
  frequency?: string | null;
};

const FREQ = [
  { value: "", label: "Sıklık (opsiyonel)" },
  { value: "as_needed", label: "Gerektiğinde" },
  { value: "weekly", label: "Haftalık" },
  { value: "biweekly", label: "İki haftada bir" },
  { value: "monthly", label: "Aylık" },
  { value: "seasonal", label: "Dönemsel" },
  { value: "occasional", label: "Ara sıra" },
];

type Props = {
  value: MaterialSelection[];
  onChange: (next: MaterialSelection[]) => void;
};

export function FarmMaterialsField({ value, onChange }: Props) {
  const [open, setOpen] = useState(true);
  const [catalog, setCatalog] = useState<AgroMaterial[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .listAgroMaterials()
      .then((rows) => {
        if (!cancelled) setCatalog(rows);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Katalog yüklenemedi");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const selected = new Set(value.map((v) => Number(v.material_id)));

  function toggle(id: number) {
    const nid = Number(id);
    if (selected.has(nid)) {
      onChange(value.filter((v) => Number(v.material_id) !== nid));
      return;
    }
    onChange([...value, { material_id: nid, frequency: null, notes: null }]);
  }

  function patch(id: number, patchVal: Partial<MaterialSelection>) {
    const nid = Number(id);
    onChange(
      value.map((v) =>
        Number(v.material_id) === nid ? { ...v, ...patchVal } : v,
      ),
    );
  }

  const fertilizers = catalog.filter((c) => c.kind === "fertilizer");
  const pps = catalog.filter((c) => c.kind === "plant_protection");
  const selectedLabels = catalog
    .filter((c) => selected.has(Number(c.id)))
    .map((c) => c.name_tr);

  return (
    <div className="rounded-lg border border-[var(--auth-border)] bg-[var(--auth-bg)]/40">
      <button
        type="button"
        className="flex w-full items-center justify-between px-3 py-2.5 text-left text-sm font-medium"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
      >
        <span>
          Bu arazide kullanılan gübre / ilaç sınıfları
          {value.length > 0 ? ` (${value.length})` : ""}
        </span>
        <span className="text-[var(--auth-muted)]">{open ? "−" : "+"}</span>
      </button>
      {value.length > 0 && !open && (
        <div className="flex flex-wrap gap-1 border-t border-[var(--auth-border)] px-3 py-2">
          {selectedLabels.length > 0
            ? selectedLabels.map((label) => (
                <span
                  key={label}
                  className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-emerald-900"
                >
                  {label}
                </span>
              ))
            : (
                <span className="text-[11px] text-[var(--auth-muted)]">
                  {value.length} sınıf seçili — açmak için +
                </span>
              )}
        </div>
      )}
      {open && (
        <div
          className="space-y-3 border-t border-[var(--auth-border)] px-3 py-3"
          onClick={(e) => e.stopPropagation()}
        >
          <p className="text-xs text-[var(--auth-muted)]">
            Eğitim amaçlı referans katalogdur. Ne kullandığınız kaydedilir; AI nem / EC /
            sulama yorumunda kullanır. Gübre veya ilaç reçetesi yazılmaz.
          </p>
          {error && <p className="text-xs text-[var(--risk-critical)]">{error}</p>}
          {loading && (
            <p className="text-xs text-[var(--auth-muted)]">Katalog yükleniyor…</p>
          )}
          {!loading && catalog.length === 0 && !error && (
            <p className="text-xs text-[var(--auth-muted)]">
              Katalog boş. API bağlantısını kontrol edin.
            </p>
          )}
          {!loading && catalog.length > 0 && (
            <>
              <Group
                title="Gübre sınıfları"
                items={fertilizers}
                selected={selected}
                value={value}
                onToggle={toggle}
                onPatch={patch}
              />
              <Group
                title="Bitki koruma (ilaç) sınıfları"
                items={pps}
                selected={selected}
                value={value}
                onToggle={toggle}
                onPatch={patch}
              />
            </>
          )}
        </div>
      )}
    </div>
  );
}

function Group({
  title,
  items,
  selected,
  value,
  onToggle,
  onPatch,
}: {
  title: string;
  items: AgroMaterial[];
  selected: Set<number>;
  value: MaterialSelection[];
  onToggle: (id: number) => void;
  onPatch: (id: number, p: Partial<MaterialSelection>) => void;
}) {
  return (
    <div>
      <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-[var(--auth-muted)]">
        {title}
      </p>
      <ul className="space-y-2">
        {items.map((m) => {
          const mid = Number(m.id);
          const on = selected.has(mid);
          const row = value.find((v) => Number(v.material_id) === mid);
          return (
            <li key={m.id} className="rounded-md border border-[var(--auth-border)]/80 p-2">
              <label className="flex cursor-pointer items-start gap-2 text-sm">
                <input
                  type="checkbox"
                  className="mt-1 size-4 accent-[var(--auth-forest)]"
                  checked={on}
                  onClick={(e) => e.stopPropagation()}
                  onChange={(e) => {
                    e.stopPropagation();
                    onToggle(mid);
                  }}
                />
                <span>
                  <span className="font-medium">{m.name_tr}</span>
                  {m.nutrient_focus && (
                    <span className="text-[var(--auth-muted)]"> · {m.nutrient_focus}</span>
                  )}
                  <span className="mt-0.5 block text-[11px] text-[var(--auth-muted)]">
                    {m.purpose}
                  </span>
                </span>
              </label>
              {on && (
                <div className="mt-2 grid gap-2 pl-6 sm:grid-cols-2">
                  <select
                    className="input text-xs"
                    value={row?.frequency || ""}
                    onClick={(e) => e.stopPropagation()}
                    onChange={(e) =>
                      onPatch(mid, { frequency: e.target.value || null })
                    }
                  >
                    {FREQ.map((f) => (
                      <option key={f.value || "none"} value={f.value}>
                        {f.label}
                      </option>
                    ))}
                  </select>
                  <input
                    className="input text-xs"
                    placeholder="Not (opsiyonel)"
                    value={row?.notes || ""}
                    onClick={(e) => e.stopPropagation()}
                    onChange={(e) => onPatch(mid, { notes: e.target.value || null })}
                  />
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
