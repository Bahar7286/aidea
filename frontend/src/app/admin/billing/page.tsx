"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "@/components/admin/AdminShell";
import { api, AdminBilling } from "@/lib/api";

export default function AdminBillingPage() {
  const [data, setData] = useState<AdminBilling | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .adminBilling()
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  const farmsPct = data
    ? Math.min(100, Math.round((data.farms_used / data.farms_limit) * 100))
    : 0;

  return (
    <AdminShell title="Abonelik ve Paket">
      {error && <p className="mb-3 text-sm text-red-700">{error}</p>}
      {data && (
        <div className="space-y-4">
          <div className="app-surface p-4">
            <p className="text-sm text-[var(--auth-muted)]">Güncel paket</p>
            <p className="text-2xl font-bold capitalize">{data.plan}</p>
            <p className="text-xs text-emerald-700">{data.status}</p>
            <p className="mt-2 text-xs text-[var(--auth-muted)]">{data.note}</p>
          </div>

          <div className="app-surface space-y-3 p-4">
            <p className="text-sm font-semibold">Kullanım özeti</p>
            {[
              {
                label: "Arazi",
                value: `${data.farms_used}/${data.farms_limit}`,
                pct: farmsPct,
              },
              {
                label: "Cihaz",
                value: `${data.devices_used}/${data.devices_limit ?? "∞"}`,
                pct: data.devices_limit
                  ? Math.min(
                      100,
                      Math.round(
                        (data.devices_used / data.devices_limit) * 100,
                      ),
                    )
                  : 40,
              },
              {
                label: "Depolama GB",
                value: `${data.storage_used_gb}/${data.storage_limit_gb}`,
                pct: Math.round(
                  (data.storage_used_gb / data.storage_limit_gb) * 100,
                ),
              },
              {
                label: "AI sorgu",
                value: `${data.ai_queries_used}/${data.ai_queries_limit}`,
                pct: Math.min(
                  100,
                  Math.round(
                    (data.ai_queries_used / data.ai_queries_limit) * 100,
                  ),
                ),
              },
            ].map((row) => (
              <div key={row.label}>
                <div className="mb-1 flex justify-between text-xs">
                  <span>{row.label}</span>
                  <span>{row.value}</span>
                </div>
                <div className="h-2 rounded-full bg-slate-200">
                  <div
                    className="h-2 rounded-full bg-[var(--auth-forest)]"
                    style={{ width: `${row.pct}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            {data.plans.map((p) => {
              const id = String(p.id);
              const name = String(p.name);
              const price = Number(p.price_try ?? 0);
              return (
                <div
                  key={id}
                  className={`app-surface p-4 ${
                    data.plan === id ? "ring-2 ring-[var(--auth-forest)]" : ""
                  }`}
                >
                  <p className="font-semibold">{name}</p>
                  <p className="text-lg font-bold">
                    {price === 0 ? "Ücretsiz" : `₺${price}`}
                  </p>
                  <ul className="mt-2 space-y-1 text-xs text-[var(--auth-muted)]">
                    {((p.features as string[]) || []).map((f) => (
                      <li key={f}>· {f}</li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>

          <div className="app-surface overflow-x-auto p-4">
            <p className="mb-2 text-sm font-semibold">Fatura geçmişi (demo)</p>
            <table className="w-full text-left text-sm">
              <thead className="text-xs text-[var(--auth-muted)]">
                <tr>
                  <th className="py-1">No</th>
                  <th className="py-1">Tarih</th>
                  <th className="py-1">Tutar</th>
                  <th className="py-1">Durum</th>
                </tr>
              </thead>
              <tbody>
                {data.invoices.map((inv) => (
                  <tr key={String(inv.no)}>
                    <td className="py-1">{String(inv.no)}</td>
                    <td className="py-1">{String(inv.date)}</td>
                    <td className="py-1">₺{String(inv.amount)}</td>
                    <td className="py-1">{String(inv.status)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </AdminShell>
  );
}
