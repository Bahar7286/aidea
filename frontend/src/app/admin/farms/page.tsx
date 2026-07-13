"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AdminShell } from "@/components/admin/AdminShell";
import { KpiCard } from "@/components/app/KpiCard";
import { api, AdminFarm } from "@/lib/api";

export default function AdminFarmsPage() {
  const [farms, setFarms] = useState<AdminFarm[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .adminFarms()
      .then(setFarms)
      .catch((err) => setError(err.message));
  }, []);

  const area = farms.reduce((s, f) => s + (f.area || 0), 0);

  return (
    <AdminShell title="Çiftlik ve Arazi Yönetimi">
      {error && <p className="mb-3 text-sm text-red-700">{error}</p>}
      <div className="mb-4 grid gap-3 sm:grid-cols-4">
        <KpiCard label="Çiftlik" value={String(farms.length)} />
        <KpiCard
          label="Aktif"
          value={String(farms.filter((f) => f.is_active).length)}
          tone="ok"
        />
        <KpiCard label="Toplam alan (da)" value={area ? String(area) : "—"} />
        <KpiCard
          label="Cihaz toplam"
          value={String(farms.reduce((s, f) => s + f.device_count, 0))}
        />
      </div>

      <ul className="space-y-3 lg:hidden">
        {farms.map((f) => (
          <li key={f.id} className="app-surface p-4">
            <p className="font-semibold">{f.name}</p>
            <p className="text-xs text-[var(--auth-muted)]">
              {f.location || "—"} · {f.owner_name}
            </p>
            <p className="mt-1 text-xs">
              {f.area ?? "—"} da · {f.device_count} cihaz · {f.zone_count} bölge
            </p>
            <Link
              href={`/farms/${f.id}`}
              className="mt-2 inline-block text-xs text-[var(--auth-forest)] hover:underline"
            >
              Aç
            </Link>
          </li>
        ))}
      </ul>

      <div className="app-surface hidden overflow-x-auto lg:block">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="text-xs text-[var(--auth-muted)]">
            <tr>
              <th className="px-3 py-2">Çiftlik</th>
              <th className="px-3 py-2">Konum</th>
              <th className="px-3 py-2">Sahip</th>
              <th className="px-3 py-2">Alan</th>
              <th className="px-3 py-2">Cihaz</th>
              <th className="px-3 py-2">Durum</th>
              <th className="px-3 py-2" />
            </tr>
          </thead>
          <tbody>
            {farms.map((f) => (
              <tr key={f.id} className="border-t border-[var(--auth-border)]">
                <td className="px-3 py-2 font-medium">{f.name}</td>
                <td className="px-3 py-2">{f.location || "—"}</td>
                <td className="px-3 py-2 text-xs">
                  {f.owner_name}
                  <br />
                  {f.owner_email}
                </td>
                <td className="px-3 py-2">{f.area ?? "—"}</td>
                <td className="px-3 py-2">{f.device_count}</td>
                <td className="px-3 py-2">
                  {f.is_active ? "Aktif" : "Pasif"}
                </td>
                <td className="px-3 py-2">
                  <Link
                    href={`/farms/${f.id}`}
                    className="text-[var(--auth-forest)] hover:underline"
                  >
                    Aç
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AdminShell>
  );
}
