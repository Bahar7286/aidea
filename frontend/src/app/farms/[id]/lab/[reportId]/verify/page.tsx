"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { AppShell } from "@/components/app/AppShell";
import { setSelectedFarmId } from "@/components/app/FarmSelector";
import { api, Farm, LabParameter, LabReport } from "@/lib/api";

function confTone(pct?: number | null) {
  if (pct == null) return "bg-slate-300";
  if (pct >= 80) return "bg-emerald-500";
  if (pct >= 50) return "bg-amber-500";
  return "bg-red-500";
}

export default function LabVerifyPage() {
  const params = useParams();
  const router = useRouter();
  const farmId = Number(params.id);
  const reportId = Number(params.reportId);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [report, setReport] = useState<LabReport | null>(null);
  const [rows, setRows] = useState<LabParameter[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!farmId || !reportId) return;
    setSelectedFarmId(farmId);
    Promise.all([api.getFarm(farmId), api.getLabDetail(reportId)])
      .then(([f, d]) => {
        setFarm(f);
        setReport(d.report);
        setRows(
          d.report.parameters.map((p) => ({
            ...p,
            parameter_code: p.parameter_code,
            value: p.value,
            unit: p.unit,
            confidence_pct: p.confidence_pct,
            extracted_auto: p.extracted_auto,
          })),
        );
      })
      .catch((err) => setError(err.message));
  }, [farmId, reportId]);

  function updateRow(idx: number, field: keyof LabParameter, value: string) {
    setRows((prev) =>
      prev.map((r, i) => {
        if (i !== idx) return r;
        if (field === "value") return { ...r, value: Number(value) };
        return { ...r, [field]: value };
      }),
    );
  }

  async function onConfirm(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.confirmLabReport(reportId, {
        confirmed: true,
        parameters: rows.map((p) => ({
          parameter_code: p.parameter_code,
          value: Number(p.value),
          unit: p.unit,
          extracted_auto: !!p.extracted_auto,
          confidence_pct: p.confidence_pct ?? null,
        })),
      });
      router.push(`/farms/${farmId}/lab/${reportId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Onay başarısız");
    } finally {
      setLoading(false);
    }
  }

  const withConf = rows.filter((r) => r.confidence_pct != null);
  const avgConf =
    withConf.length > 0
      ? Math.round(
          withConf.reduce((s, r) => s + (r.confidence_pct || 0), 0) /
            withConf.length,
        )
      : report?.extraction_confidence != null
        ? Math.round(report.extraction_confidence)
        : null;
  const okCount = rows.filter(
    (r) => r.confidence_pct == null || (r.confidence_pct ?? 0) >= 50,
  ).length;

  return (
    <AppShell title="Analiz Değerlerini Doğrula" farmName={farm?.name}>
      <div className="mb-4">
        <Link
          href={`/farms/${farmId}/lab`}
          className="text-sm text-[var(--auth-forest)] hover:underline"
        >
          ← Analizler
        </Link>
      </div>

      {error && (
        <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>
      )}

      {(avgConf != null || report) && (
        <div className="app-surface mb-4 grid gap-2 p-4 sm:grid-cols-2">
          <div>
            <p className="text-xs text-[var(--auth-muted)]">Veri okuma güveni</p>
            <p className="text-2xl font-bold">
              {avgConf != null ? `%${avgConf}` : "Manuel"}
            </p>
          </div>
          <div>
            <p className="text-xs text-[var(--auth-muted)]">Okunan değer</p>
            <p className="text-2xl font-bold">
              {okCount}/{rows.length}
            </p>
          </div>
          <p className="sm:col-span-2 text-xs text-[var(--auth-muted)]">
            Simüle çıkarım gerçek OCR değildir. Değerleri kontrol edip onaylayın.
          </p>
        </div>
      )}

      <form onSubmit={onConfirm} className="space-y-4">
        <div className="app-surface overflow-x-auto">
          <table className="w-full min-w-[520px] text-left text-sm">
            <thead className="border-b border-[var(--auth-border)] text-xs text-[var(--auth-muted)]">
              <tr>
                <th className="px-3 py-2 font-medium">Parametre</th>
                <th className="px-3 py-2 font-medium">Değer</th>
                <th className="px-3 py-2 font-medium">Birim</th>
                <th className="px-3 py-2 font-medium">Güven</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, idx) => (
                <tr
                  key={`${r.parameter_code}-${idx}`}
                  className="border-b border-[var(--auth-border)] last:border-0"
                >
                  <td className="px-3 py-2 font-medium uppercase">
                    {r.parameter_code}
                  </td>
                  <td className="px-3 py-2">
                    <input
                      className="input py-1.5"
                      type="number"
                      step="0.01"
                      value={r.value}
                      onChange={(e) => updateRow(idx, "value", e.target.value)}
                      required
                    />
                  </td>
                  <td className="px-3 py-2">
                    <input
                      className="input py-1.5"
                      value={r.unit}
                      onChange={(e) => updateRow(idx, "unit", e.target.value)}
                      required
                    />
                  </td>
                  <td className="px-3 py-2">
                    <span className="inline-flex items-center gap-2 text-xs">
                      <span
                        className={`h-2 w-2 rounded-full ${confTone(r.confidence_pct)}`}
                      />
                      {r.confidence_pct != null ? `%${r.confidence_pct}` : "—"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex flex-wrap gap-2">
          <Link
            href={`/farms/${farmId}/lab/new`}
            className="btn btn-secondary text-sm"
          >
            Geri
          </Link>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "…" : "Onayla"}
          </button>
        </div>
      </form>
    </AppShell>
  );
}
