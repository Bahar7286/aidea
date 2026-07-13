"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/app/AppShell";
import { FarmSelector, setSelectedFarmId } from "@/components/app/FarmSelector";
import { TwinMapPanel, TwinZone } from "@/components/app/TwinMapPanel";
import { api, TwinView } from "@/lib/api";

export default function TwinPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const [data, setData] = useState<TwinView | null>(null);
  const [selected, setSelected] = useState<string | undefined>();
  const [error, setError] = useState("");

  useEffect(() => {
    if (!farmId) return;
    setSelectedFarmId(farmId);
    api
      .farmTwin(farmId)
      .then((d) => {
        setData(d);
        setSelected(d.zones[0]?.name);
      })
      .catch((err) => setError(err.message));
  }, [farmId]);

  return (
    <AppShell title="Dijital İkiz Haritası" farmName={data?.farm.name}>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <FarmSelector farmId={farmId} suffixPath="/twin" />
        <Link href={`/farms/${farmId}/sensors/live`} className="btn btn-secondary text-sm">
          Canlı sensör
        </Link>
        <Link href={`/farms/${farmId}/zones`} className="btn btn-ghost text-sm">
          Bölgeler
        </Link>
      </div>
      {error && <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>}
      {data ? (
        <TwinMapPanel
          zones={data.zones as TwinZone[]}
          selectedName={selected}
          onSelect={(z) => setSelected(z.name)}
          insight={data.insight}
          sourceLabel={data.source_label}
          confidence={data.confidence}
        />
      ) : (
        <p className="text-sm text-[var(--auth-muted)]">Harita yükleniyor...</p>
      )}
    </AppShell>
  );
}
