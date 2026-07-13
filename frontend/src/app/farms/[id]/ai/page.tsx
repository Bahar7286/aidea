"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app/AppShell";
import { FarmSelector, setSelectedFarmId } from "@/components/app/FarmSelector";
import { KpiCard } from "@/components/app/KpiCard";
import { api, Farm, RecommendationSummary } from "@/lib/api";

const CATEGORIES = [
  { id: "all", label: "Tümü" },
  { id: "irrigation", label: "Sulama" },
  { id: "climate", label: "İklim" },
  { id: "other", label: "Diğer" },
  { id: "fertilizer", label: "Gübreleme" },
  { id: "disease", label: "Hastalık" },
] as const;

function priTone(p: string) {
  if (p === "high") return "bg-red-100 text-red-800";
  if (p === "medium") return "bg-amber-100 text-amber-900";
  return "bg-emerald-100 text-emerald-800";
}

function priLabel(p: string) {
  if (p === "high") return "Yüksek";
  if (p === "medium") return "Orta";
  return "Düşük";
}

export default function AiRecommendationsPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [data, setData] = useState<RecommendationSummary | null>(null);
  const [category, setCategory] = useState("all");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function load(cat = category) {
    const [f, rec] = await Promise.all([
      api.getFarm(farmId),
      api.listRecommendations(farmId, {
        category: cat === "all" ? undefined : cat,
      }),
    ]);
    setFarm(f);
    setData(rec);
  }

  useEffect(() => {
    if (!farmId) return;
    setSelectedFarmId(farmId);
    load().catch((err) => setError(err.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [farmId]);

  async function refreshPredict() {
    setBusy(true);
    setError("");
    try {
      await api.predict(farmId);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Tahmin başarısız");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell title="AI Önerileri" farmName={farm?.name}>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <FarmSelector farmId={farmId} suffixPath="/ai" />
        <button
          type="button"
          className="btn btn-secondary text-sm"
          onClick={refreshPredict}
          disabled={busy}
        >
          {busy ? "…" : "Yeniden analiz et"}
        </button>
        <Link href={`/farms/${farmId}/irrigation`} className="btn btn-ghost text-sm">
          Sulama
        </Link>
      </div>

      {error && (
        <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>
      )}

      <div className="mb-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard label="Tümü" value={String(data?.total ?? "—")} />
        <KpiCard
          label="Yüksek öncelik"
          value={String(data?.high ?? "—")}
          tone={data && data.high > 0 ? "warn" : undefined}
        />
        <KpiCard label="Orta öncelik" value={String(data?.medium ?? "—")} />
        <KpiCard
          label="Düşük öncelik"
          value={String(data?.low ?? "—")}
          tone="ok"
        />
      </div>

      <div className="mb-4 flex gap-2 overflow-x-auto pb-1">
        {CATEGORIES.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => {
              setCategory(c.id);
              load(c.id).catch((err) => setError(err.message));
            }}
            className={`shrink-0 rounded-full px-3 py-1.5 text-xs font-semibold ${
              category === c.id
                ? "bg-[var(--auth-forest)] text-white"
                : "bg-white text-[var(--auth-muted)] ring-1 ring-[var(--auth-border)]"
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      {(category === "fertilizer" || category === "disease") && (
        <p className="mb-3 rounded-xl bg-slate-100 px-3 py-2 text-xs text-[var(--auth-muted)]">
          Bu kategori MVP kapsamı dışındadır (nem + sulama odaklı).
        </p>
      )}

      <ul className="space-y-3">
        {(data?.items || []).map((item) => {
          const href = item.prediction_id
            ? `/farms/${farmId}/ai/${item.prediction_id}`
            : `/farms/${farmId}/hub`;
          return (
            <li key={item.id}>
              <Link href={href} className="app-surface block p-4 transition hover:bg-emerald-50/40">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold">{item.title}</p>
                    <p className="mt-1 text-sm text-[var(--auth-muted)]">
                      {item.summary}
                    </p>
                  </div>
                  <span
                    className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${priTone(item.priority)}`}
                  >
                    {priLabel(item.priority)}
                  </span>
                </div>
                <div className="mt-2 flex flex-wrap gap-2 text-[11px] text-[var(--auth-muted)]">
                  <span className="uppercase">{item.category}</span>
                  {item.confidence_score != null && (
                    <span>Güven %{item.confidence_score.toFixed(0)}</span>
                  )}
                  {item.created_at && (
                    <span>
                      {new Date(item.created_at).toLocaleString("tr-TR")}
                    </span>
                  )}
                  {item.automation_allowed && (
                    <span className="font-semibold text-emerald-800">
                      Otomasyon uygun
                    </span>
                  )}
                </div>
              </Link>
            </li>
          );
        })}
        {data && data.items.length === 0 && (
          <li className="rounded-2xl border border-dashed border-[var(--auth-border)] p-8 text-center text-sm text-[var(--auth-muted)]">
            Öneri yok. Önce sensör verisi girip analiz çalıştırın.
          </li>
        )}
      </ul>
    </AppShell>
  );
}
