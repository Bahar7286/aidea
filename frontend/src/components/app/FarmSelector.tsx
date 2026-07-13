"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, Farm } from "@/lib/api";

const KEY = "agritwin_selected_farm";

export function getSelectedFarmId(): number | null {
  if (typeof window === "undefined") return null;
  const v = localStorage.getItem(KEY);
  return v ? Number(v) : null;
}

export function setSelectedFarmId(id: number) {
  localStorage.setItem(KEY, String(id));
}

/** Farm dropdown; persists selection and can redirect between farm-scoped routes. */
export function FarmSelector({
  farmId,
  onChange,
  suffixPath = "",
}: {
  farmId?: number | null;
  onChange?: (id: number) => void;
  /** e.g. "/twin" → navigates to /farms/{id}/twin when selection changes */
  suffixPath?: string;
}) {
  const router = useRouter();
  const [farms, setFarms] = useState<Farm[]>([]);
  const [value, setValue] = useState<number | "">(farmId ?? "");

  useEffect(() => {
    api.listFarms().then((rows) => {
      setFarms(rows);
      const preferred = farmId || getSelectedFarmId() || rows[0]?.id;
      if (preferred) {
        setValue(preferred);
        setSelectedFarmId(preferred);
      }
    });
  }, [farmId]);

  useEffect(() => {
    if (farmId) setValue(farmId);
  }, [farmId]);

  function select(id: number) {
    setValue(id);
    setSelectedFarmId(id);
    onChange?.(id);
    if (suffixPath !== undefined && suffixPath !== null) {
      router.push(`/farms/${id}${suffixPath}`);
    }
  }

  if (farms.length === 0) {
    return (
      <Link href="/farms/new" className="text-sm font-medium text-[var(--auth-forest)]">
        Arazi ekle →
      </Link>
    );
  }

  return (
    <select
      className="input max-w-[220px] text-sm"
      value={value}
      onChange={(e) => select(Number(e.target.value))}
      aria-label="Arazi seç"
    >
      {farms.map((f) => (
        <option key={f.id} value={f.id}>
          {f.name}
        </option>
      ))}
    </select>
  );
}
