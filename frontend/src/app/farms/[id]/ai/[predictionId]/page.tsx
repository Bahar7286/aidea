"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app/AppShell";
import { setSelectedFarmId } from "@/components/app/FarmSelector";
import { MoistureSparkline } from "@/components/app/MoistureSparkline";
import {
  api,
  Farm,
  RecommendationDetail,
} from "@/lib/api";

export default function AiDetailPage() {
  const params = useParams();
  const router = useRouter();
  const farmId = Number(params.id);
  const predictionId = Number(params.predictionId);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [detail, setDetail] = useState<RecommendationDetail | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);

  useEffect(() => {
    if (!farmId || !predictionId) return;
    setSelectedFarmId(farmId);
    Promise.all([
      api.getFarm(farmId),
      api.getRecommendationDetail(predictionId),
    ])
      .then(([f, d]) => {
        setFarm(f);
        setDetail(d);
      })
      .catch((err) => setError(err.message));
  }, [farmId, predictionId]);

  async function applyIrrigation() {
    if (!detail?.can_apply) return;
    setBusy(true);
    setError("");
    try {
      await api.startIrrigation(
        farmId,
        detail.prediction.irrigation_duration ?? undefined,
      );
      setConfirmOpen(false);
      router.push(`/farms/${farmId}/irrigation`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sulama başlatılamadı");
    } finally {
      setBusy(false);
    }
  }

  const p = detail?.prediction;

  return (
    <AppShell title="AI Öneri Detayı" farmName={farm?.name}>
      <div className="mb-4">
        <Link
          href={`/farms/${farmId}/ai`}
          className="text-sm text-[var(--auth-forest)] hover:underline"
        >
          ← AI önerileri
        </Link>
      </div>

      {error && (
        <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>
      )}

      {!detail || !p ? (
        <p className="text-sm text-[var(--auth-muted)]">Yükleniyor…</p>
      ) : (
        <div className="space-y-4 pb-24">
          <div className="app-surface p-4">
            <h1 className="text-xl font-bold">{detail.title}</h1>
            <p className="mt-2 text-sm text-[var(--auth-muted)]">
              {p.explanation}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              {
                label: "Toprak nemi",
                value:
                  detail.current_moisture != null
                    ? `%${detail.current_moisture}`
                    : "—",
              },
              {
                label: "Su ihtiyacı",
                value:
                  detail.estimated_water_mm != null
                    ? `${detail.estimated_water_mm} mm`
                    : "—",
              },
              {
                label: "Süre",
                value: p.irrigation_duration
                  ? `${p.irrigation_duration} dk`
                  : "—",
              },
              {
                label: "Güven",
                value: `%${p.confidence_score.toFixed(0)}`,
              },
            ].map((m) => (
              <div key={m.label} className="app-surface p-3">
                <p className="text-[11px] text-[var(--auth-muted)]">{m.label}</p>
                <p className="text-lg font-bold">{m.value}</p>
              </div>
            ))}
          </div>

          <div className="app-surface space-y-2 p-4">
            <p className="text-sm font-semibold">AI açıklaması</p>
            <ul className="list-decimal space-y-1 pl-5 text-sm text-[var(--auth-muted)]">
              {detail.factors.map((f) => (
                <li key={f}>{f}</li>
              ))}
            </ul>
            <div className="pt-3">
              <MoistureSparkline
                points={[
                  detail.current_moisture,
                  p.moisture_24h,
                  p.moisture_48h,
                  p.moisture_72h,
                ]}
              />
            </div>
          </div>

          <div className="app-surface space-y-2 p-4">
            <p className="text-sm font-semibold">Veri dayanakları</p>
            <ul className="space-y-1 text-sm text-[var(--auth-muted)]">
              {detail.data_sources.map((s) => (
                <li key={s}>· {s}</li>
              ))}
            </ul>
          </div>

          {!detail.can_apply && detail.apply_block_reason && (
            <p className="rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-950">
              {detail.apply_block_reason}
            </p>
          )}

          <div className="fixed inset-x-0 bottom-16 z-30 border-t border-[var(--auth-border)] bg-white/95 p-3 backdrop-blur lg:static lg:border-0 lg:bg-transparent lg:p-0">
            <div className="mx-auto flex max-w-3xl flex-wrap gap-2">
              <Link
                href={`/farms/${farmId}/scenarios`}
                className="btn btn-secondary text-sm"
              >
                Senaryo simülatörü
              </Link>
              <button
                type="button"
                className="btn btn-primary text-sm"
                disabled={!detail.can_apply || busy}
                onClick={() => setConfirmOpen(true)}
              >
                Uygula (sanal sulama)
              </button>
            </div>
          </div>
        </div>
      )}

      {confirmOpen && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-4 sm:items-center">
          <div className="app-surface w-full max-w-md space-y-3 p-5">
            <p className="font-semibold">Sanal sulamayı onaylıyor musunuz?</p>
            <p className="text-sm text-[var(--auth-muted)]">
              Gerçek vana yoktur. Onayınız olmadan sulama başlamaz.
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                className="btn btn-secondary flex-1"
                onClick={() => setConfirmOpen(false)}
              >
                Vazgeç
              </button>
              <button
                type="button"
                className="btn btn-primary flex-1"
                disabled={busy}
                onClick={applyIrrigation}
              >
                {busy ? "…" : "Onayla"}
              </button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
