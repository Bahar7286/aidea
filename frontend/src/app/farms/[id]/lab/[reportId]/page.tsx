"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app/AppShell";
import { setSelectedFarmId } from "@/components/app/FarmSelector";
import { api, Farm, LabDetail } from "@/lib/api";

function statusLabel(s?: string | null) {
  if (s === "verified") return "Doğrulandı";
  if (s === "pending") return "Bekliyor";
  if (s === "missing") return "Eksik";
  return s || "—";
}

export default function LabDetailPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const reportId = Number(params.reportId);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [detail, setDetail] = useState<LabDetail | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!farmId || !reportId) return;
    setSelectedFarmId(farmId);
    Promise.all([api.getFarm(farmId), api.getLabDetail(reportId)])
      .then(([f, d]) => {
        setFarm(f);
        setDetail(d);
      })
      .catch((err) => setError(err.message));
  }, [farmId, reportId]);

  const r = detail?.report;
  const highlight = (detail?.insights || []).filter((i) =>
    ["ph", "ec", "om", "p", "k", "lime"].includes(i.parameter_code),
  );

  return (
    <AppShell title="Analiz Detayı" farmName={farm?.name}>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <Link
          href={`/farms/${farmId}/lab`}
          className="text-sm text-[var(--auth-forest)] hover:underline"
        >
          ← Analizler
        </Link>
        {r && (
          <span
            className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
              r.status === "verified"
                ? "bg-emerald-100 text-emerald-800"
                : r.status === "pending"
                  ? "bg-amber-100 text-amber-900"
                  : "bg-red-100 text-red-800"
            }`}
          >
            {statusLabel(r.status)}
          </span>
        )}
        {r && !r.user_confirmed && (
          <Link
            href={`/farms/${farmId}/lab/${reportId}/verify`}
            className="btn btn-secondary text-xs"
          >
            Doğrulamaya git
          </Link>
        )}
      </div>

      {error && (
        <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>
      )}

      {!r || !detail ? (
        <p className="text-sm text-[var(--auth-muted)]">Yükleniyor…</p>
      ) : (
        <div className="space-y-4">
          <div className="app-surface p-4">
            <h1 className="text-xl font-bold">
              {r.report_number || `Rapor #${r.id}`}
            </h1>
            <p className="text-sm text-[var(--auth-muted)]">
              {r.lab_name}
              {r.sample_region ? ` · ${r.sample_region}` : ""}
              {r.sample_depth_cm ? ` · ${r.sample_depth_cm} cm` : ""}
              {" · "}
              {r.sample_date
                ? new Date(r.sample_date).toLocaleDateString("tr-TR")
                : new Date(r.created_at).toLocaleDateString("tr-TR")}
            </p>
            <p className="mt-2 text-xs text-[var(--auth-muted)]">
              {detail.source_note}
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-6">
            {highlight.slice(0, 6).map((i) => (
              <div key={i.parameter_code} className="app-surface p-3">
                <p className="text-[11px] text-[var(--auth-muted)]">{i.label}</p>
                <p className="text-lg font-bold">
                  {i.value}
                  <span className="ml-1 text-xs font-normal text-[var(--auth-muted)]">
                    {i.unit}
                  </span>
                </p>
                <p
                  className={`mt-1 text-[10px] font-bold ${
                    i.tone === "ok"
                      ? "text-emerald-700"
                      : i.tone === "critical"
                        ? "text-red-700"
                        : "text-amber-800"
                  }`}
                >
                  {i.status_label}
                </p>
              </div>
            ))}
          </div>

          {(detail.insights.some((i) => i.risk === "high") ||
            detail.insights.some((i) => i.risk === "medium")) && (
            <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950">
              {detail.insights
                .filter((i) => i.risk === "high" || i.risk === "medium")
                .slice(0, 2)
                .map((i) => i.message)
                .join(" ")}
            </div>
          )}

          <div className="grid gap-4 lg:grid-cols-[1fr_260px]">
            <div className="app-surface space-y-3 p-4">
              <p className="text-sm font-semibold">AgriTwin AI yorumu</p>
              <p className="text-sm text-[var(--auth-muted)]">
                {detail.ai_summary}
              </p>
              <ul className="space-y-2">
                {detail.insights.map((i) => (
                  <li
                    key={i.parameter_code}
                    className="border-l-2 border-[var(--auth-forest)] pl-3 text-sm"
                  >
                    <span className="font-medium">{i.label}</span>
                    <span className="text-[var(--auth-muted)]">
                      {" "}
                      · {i.status_label} ({i.risk})
                    </span>
                    <p className="text-xs text-[var(--auth-muted)]">{i.message}</p>
                  </li>
                ))}
              </ul>
              <p className="text-[11px] text-[var(--auth-muted)]">
                Gübre / ilaç reçetesi değildir. Sulama ve nem kararında laboratuvar
                profili destek kayıttır.
              </p>
            </div>

            <aside className="app-surface h-fit space-y-2 p-4 text-sm">
              <p className="font-semibold">Rapor bilgileri</p>
              <dl className="space-y-2 text-xs text-[var(--auth-muted)]">
                <div className="flex justify-between gap-2">
                  <dt>Lab</dt>
                  <dd className="text-[var(--auth-ink)]">{r.lab_name}</dd>
                </div>
                <div className="flex justify-between gap-2">
                  <dt>Kaynak</dt>
                  <dd className="text-[var(--auth-ink)]">{r.source_type}</dd>
                </div>
                <div className="flex justify-between gap-2">
                  <dt>Dosya</dt>
                  <dd className="truncate text-[var(--auth-ink)]">
                    {r.file_name || "—"}
                  </dd>
                </div>
                <div className="flex justify-between gap-2">
                  <dt>Onay</dt>
                  <dd className="text-[var(--auth-ink)]">
                    {r.user_confirmed ? "Evet" : "Hayır"}
                  </dd>
                </div>
              </dl>
              <div className="overflow-x-auto pt-2">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="text-[var(--auth-muted)]">
                      <th className="py-1">Kod</th>
                      <th className="py-1">Değer</th>
                    </tr>
                  </thead>
                  <tbody>
                    {r.parameters.map((p) => (
                      <tr key={p.id ?? p.parameter_code}>
                        <td className="py-1 font-medium uppercase">
                          {p.parameter_code}
                        </td>
                        <td className="py-1">
                          {p.value} {p.unit}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </aside>
          </div>
        </div>
      )}
    </AppShell>
  );
}
