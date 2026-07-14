"use client";

import { useEffect, useState } from "react";
import { api, AgroMaterial } from "@/lib/api";

export type MaterialSelection = {
  material_id: number;
  notes?: string | null;
  frequency?: string | null;
  last_applied_at?: string | null;
  is_last_fertilizer?: boolean;
  is_last_pesticide?: boolean;
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
  /** Compact panel without collapse (farm detail / hub). */
  alwaysOpen?: boolean;
  title?: string;
};

function toDateInput(iso: string | null | undefined): string {
  if (!iso) return "";
  return iso.slice(0, 10);
}

function fromDateInput(d: string): string | null {
  if (!d) return null;
  return `${d}T12:00:00`;
}

export function FarmMaterialsField({
  value,
  onChange,
  alwaysOpen = false,
  title = "Bu arazide kullanılan gübre / ilaç sınıfları",
}: Props) {
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
  const fertilizers = catalog.filter((c) => c.kind === "fertilizer");
  const pps = catalog.filter((c) => c.kind === "plant_protection");

  const lastFertId =
    value.find((v) => v.is_last_fertilizer)?.material_id ?? "";
  const lastPestId =
    value.find((v) => v.is_last_pesticide)?.material_id ?? "";
  const lastFertDate = toDateInput(
    value.find((v) => v.is_last_fertilizer)?.last_applied_at,
  );
  const lastPestDate = toDateInput(
    value.find((v) => v.is_last_pesticide)?.last_applied_at,
  );

  const selectedLabels = catalog
    .filter((c) => selected.has(Number(c.id)))
    .map((c) => c.name_tr);

  function toggle(id: number) {
    const nid = Number(id);
    if (selected.has(nid)) {
      onChange(value.filter((v) => Number(v.material_id) !== nid));
      return;
    }
    onChange([
      ...value,
      {
        material_id: nid,
        frequency: null,
        notes: null,
        last_applied_at: null,
        is_last_fertilizer: false,
        is_last_pesticide: false,
      },
    ]);
  }

  function patch(id: number, patchVal: Partial<MaterialSelection>) {
    const nid = Number(id);
    onChange(
      value.map((v) =>
        Number(v.material_id) === nid ? { ...v, ...patchVal } : v,
      ),
    );
  }

  function ensureMaterial(
    mid: number,
    extras: Partial<MaterialSelection> = {},
  ): MaterialSelection[] {
    const exists = value.find((v) => Number(v.material_id) === mid);
    if (exists) {
      return value.map((v) =>
        Number(v.material_id) === mid ? { ...v, ...extras } : v,
      );
    }
    return [
      ...value,
      {
        material_id: mid,
        frequency: null,
        notes: null,
        last_applied_at: null,
        is_last_fertilizer: false,
        is_last_pesticide: false,
        ...extras,
      },
    ];
  }

  function setLastFertilizer(midStr: string) {
    if (!midStr) {
      onChange(
        value.map((v) => ({
          ...v,
          is_last_fertilizer: false,
        })),
      );
      return;
    }
    const mid = Number(midStr);
    let next = ensureMaterial(mid, { is_last_fertilizer: true });
    next = next.map((v) => ({
      ...v,
      is_last_fertilizer: Number(v.material_id) === mid,
    }));
    onChange(next);
  }

  function setLastPesticide(midStr: string) {
    if (!midStr) {
      onChange(
        value.map((v) => ({
          ...v,
          is_last_pesticide: false,
        })),
      );
      return;
    }
    const mid = Number(midStr);
    let next = ensureMaterial(mid, { is_last_pesticide: true });
    next = next.map((v) => ({
      ...v,
      is_last_pesticide: Number(v.material_id) === mid,
    }));
    onChange(next);
  }

  function setLastFertDate(d: string) {
    const mid = lastFertId ? Number(lastFertId) : null;
    if (!mid) return;
    onChange(
      value.map((v) =>
        Number(v.material_id) === mid
          ? { ...v, last_applied_at: fromDateInput(d) }
          : v,
      ),
    );
  }

  function setLastPestDate(d: string) {
    const mid = lastPestId ? Number(lastPestId) : null;
    if (!mid) return;
    onChange(
      value.map((v) =>
        Number(v.material_id) === mid
          ? { ...v, last_applied_at: fromDateInput(d) }
          : v,
      ),
    );
  }

  const showBody = alwaysOpen || open;

  return (
    <div className="rounded-lg border border-[var(--auth-border)] bg-[var(--auth-bg)]/40">
      {!alwaysOpen && (
        <button
          type="button"
          className="flex w-full items-center justify-between px-3 py-2.5 text-left text-sm font-medium"
          onClick={() => setOpen((o) => !o)}
          aria-expanded={open}
        >
          <span>
            {title}
            {value.length > 0 ? ` (${value.length})` : ""}
          </span>
          <span className="text-[var(--auth-muted)]">{open ? "−" : "+"}</span>
        </button>
      )}
      {alwaysOpen && (
        <div className="px-3 pt-3">
          <p className="text-sm font-medium">{title}</p>
        </div>
      )}
      {value.length > 0 && !showBody && (
        <div className="flex flex-wrap gap-1 border-t border-[var(--auth-border)] px-3 py-2">
          {selectedLabels.length > 0 ? (
            selectedLabels.map((label) => (
              <span
                key={label}
                className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-emerald-900"
              >
                {label}
              </span>
            ))
          ) : (
            <span className="text-[11px] text-[var(--auth-muted)]">
              {value.length} sınıf seçili — açmak için +
            </span>
          )}
        </div>
      )}
      {showBody && (
        <div
          className="space-y-3 border-t border-[var(--auth-border)] px-3 py-3"
          onClick={(e) => e.stopPropagation()}
        >
          <p className="text-xs text-[var(--auth-muted)]">
            Eğitim amaçlı referans katalogdur. Ne kullandığınız ve son uygulanan
            sınıf kaydedilir; AI nem / EC / sulama yorumunda kullanır. Gübre veya
            ilaç reçetesi yazılmaz.
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
              <div className="space-y-2 rounded-md border border-emerald-200/80 bg-emerald-50/40 p-3">
                <p className="text-xs font-semibold uppercase tracking-wide text-emerald-900">
                  Son kullanılan (AI bağlamı)
                </p>
                <div className="grid gap-2 sm:grid-cols-2">
                  <label className="block text-xs">
                    <span className="text-[var(--auth-muted)]">
                      Son kullanılan gübre
                    </span>
                    <select
                      className="input mt-1 text-xs"
                      value={lastFertId === "" ? "" : String(lastFertId)}
                      onChange={(e) => setLastFertilizer(e.target.value)}
                    >
                      <option value="">Seçilmedi</option>
                      {fertilizers.map((m) => (
                        <option key={m.id} value={m.id}>
                          {m.name_tr}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="block text-xs">
                    <span className="text-[var(--auth-muted)]">
                      Uygulama tarihi (opsiyonel)
                    </span>
                    <input
                      type="date"
                      className="input mt-1 text-xs"
                      value={lastFertDate}
                      disabled={!lastFertId}
                      onChange={(e) => setLastFertDate(e.target.value)}
                    />
                  </label>
                  <label className="block text-xs">
                    <span className="text-[var(--auth-muted)]">
                      Son kullanılan ilaç
                    </span>
                    <select
                      className="input mt-1 text-xs"
                      value={lastPestId === "" ? "" : String(lastPestId)}
                      onChange={(e) => setLastPesticide(e.target.value)}
                    >
                      <option value="">Seçilmedi</option>
                      {pps.map((m) => (
                        <option key={m.id} value={m.id}>
                          {m.name_tr}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="block text-xs">
                    <span className="text-[var(--auth-muted)]">
                      Uygulama tarihi (opsiyonel)
                    </span>
                    <input
                      type="date"
                      className="input mt-1 text-xs"
                      value={lastPestDate}
                      disabled={!lastPestId}
                      onChange={(e) => setLastPestDate(e.target.value)}
                    />
                  </label>
                </div>
              </div>

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
          const badges: string[] = [];
          if (row?.is_last_fertilizer) badges.push("Son gübre");
          if (row?.is_last_pesticide) badges.push("Son ilaç");
          return (
            <li
              key={m.id}
              className="rounded-md border border-[var(--auth-border)]/80 p-2"
            >
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
                    <span className="text-[var(--auth-muted)]">
                      {" "}
                      · {m.nutrient_focus}
                    </span>
                  )}
                  {badges.map((b) => (
                    <span
                      key={b}
                      className="ml-1 rounded-full bg-amber-100 px-1.5 py-0.5 text-[9px] font-semibold text-amber-900"
                    >
                      {b}
                    </span>
                  ))}
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
                    onChange={(e) =>
                      onPatch(mid, { notes: e.target.value || null })
                    }
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
