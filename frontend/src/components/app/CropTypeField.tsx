"use client";

import { useEffect, useState } from "react";

export const CROP_OPTIONS = [
  { value: "domates", label: "Domates" },
  { value: "biber", label: "Biber" },
  { value: "salatalik", label: "Salatalık" },
  { value: "patlican", label: "Patlıcan" },
  { value: "marul", label: "Marul" },
  { value: "fasulye", label: "Fasulye" },
  { value: "misir", label: "Mısır" },
  { value: "bugday", label: "Buğday" },
  { value: "arpa", label: "Arpa" },
  { value: "aycicegi", label: "Ayçiçeği" },
  { value: "pamuk", label: "Pamuk" },
  { value: "uzum", label: "Üzüm" },
  { value: "zeytin", label: "Zeytin" },
  { value: "cilek", label: "Çilek" },
  { value: "patates", label: "Patates" },
  { value: "sogan", label: "Soğan" },
] as const;

const CUSTOM = "__custom__";

type Props = {
  id?: string;
  name?: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  className?: string;
};

export function CropTypeField({
  id = "crop_type",
  name = "crop_type",
  value,
  onChange,
  required,
  className = "input",
}: Props) {
  const known = CROP_OPTIONS.some((c) => c.value === value);
  const [mode, setMode] = useState<string>(known || !value ? value || "domates" : CUSTOM);
  const [custom, setCustom] = useState(known || !value ? "" : value);

  useEffect(() => {
    const isKnown = CROP_OPTIONS.some((c) => c.value === value);
    if (isKnown) {
      setMode(value);
      setCustom("");
    } else if (value) {
      setMode(CUSTOM);
      setCustom(value);
    }
  }, [value]);

  return (
    <div className="space-y-2">
      <select
        className={className}
        id={id}
        value={mode}
        required={required && mode !== CUSTOM}
        onChange={(e) => {
          const next = e.target.value;
          setMode(next);
          if (next === CUSTOM) {
            onChange(custom.trim() || "");
          } else {
            onChange(next);
          }
        }}
      >
        {CROP_OPTIONS.map((c) => (
          <option key={c.value} value={c.value}>
            {c.label}
          </option>
        ))}
        <option value={CUSTOM}>Diğer / özel ürün…</option>
      </select>
      {mode === CUSTOM && (
        <input
          className={className}
          name={name}
          value={custom}
          required={required}
          placeholder="Örn. kavun, ıspanak…"
          maxLength={80}
          onChange={(e) => {
            const v = e.target.value;
            setCustom(v);
            onChange(v.trim());
          }}
        />
      )}
      {mode !== CUSTOM && <input type="hidden" name={name} value={value} />}
    </div>
  );
}
