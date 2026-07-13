"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "@/components/admin/AdminShell";
import { KpiCard } from "@/components/app/KpiCard";
import { api, AdminDevice } from "@/lib/api";

export default function AdminDevicesPage() {
  const [devices, setDevices] = useState<AdminDevice[]>([]);
  const [filter, setFilter] = useState("all");
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .adminDevices({
        status: filter === "all" ? undefined : filter,
      })
      .then(setDevices)
      .catch((err) => setError(err.message));
  }, [filter]);

  const online = devices.filter((d) =>
    ["active", "online", "normal"].includes(
      (d.connection_status || "").toLowerCase(),
    ),
  ).length;
  const lowBatt = devices.filter(
    (d) => d.battery_percent != null && d.battery_percent < 20,
  ).length;

  return (
    <AdminShell title="Sensör ve Cihaz Filosu">
      {error && <p className="mb-3 text-sm text-red-700">{error}</p>}
      <div className="mb-4 grid gap-3 sm:grid-cols-4">
        <KpiCard label="Toplam" value={String(devices.length)} />
        <KpiCard label="Çevrimiçi" value={String(online)} tone="ok" />
        <KpiCard
          label="Çevrimdışı"
          value={String(Math.max(0, devices.length - online))}
          tone="warn"
        />
        <KpiCard
          label="Düşük pil"
          value={String(lowBatt)}
          tone={lowBatt ? "warn" : undefined}
        />
      </div>

      <div className="mb-4 flex gap-2">
        {(["all", "online", "offline"] as const).map((f) => (
          <button
            key={f}
            type="button"
            onClick={() => setFilter(f)}
            className={`rounded-full px-3 py-1.5 text-xs font-semibold ${
              filter === f
                ? "bg-[var(--auth-forest)] text-white"
                : "bg-white ring-1 ring-[var(--auth-border)]"
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      <ul className="space-y-3 lg:hidden">
        {devices.map((d) => (
          <li key={d.id} className="app-surface p-4 text-sm">
            <p className="font-semibold">{d.device_name}</p>
            <p className="text-xs text-[var(--auth-muted)]">
              {d.farm_name} · {d.device_type}
            </p>
            <p className="mt-1 text-xs">
              {d.connection_status} · nem{" "}
              {d.last_moisture != null ? `%${d.last_moisture}` : "—"} · pil{" "}
              {d.battery_percent ?? "—"}%
            </p>
          </li>
        ))}
      </ul>

      <div className="app-surface hidden overflow-x-auto lg:block">
        <table className="w-full min-w-[800px] text-left text-sm">
          <thead className="text-xs text-[var(--auth-muted)]">
            <tr>
              <th className="px-3 py-2">Cihaz</th>
              <th className="px-3 py-2">Seri</th>
              <th className="px-3 py-2">Tür</th>
              <th className="px-3 py-2">Çiftlik</th>
              <th className="px-3 py-2">Pil</th>
              <th className="px-3 py-2">Durum</th>
              <th className="px-3 py-2">Son nem</th>
            </tr>
          </thead>
          <tbody>
            {devices.map((d) => (
              <tr key={d.id} className="border-t border-[var(--auth-border)]">
                <td className="px-3 py-2 font-medium">{d.device_name}</td>
                <td className="px-3 py-2 text-xs">{d.serial_number || "—"}</td>
                <td className="px-3 py-2">{d.device_type}</td>
                <td className="px-3 py-2">{d.farm_name}</td>
                <td className="px-3 py-2">
                  {d.battery_percent != null ? `${d.battery_percent}%` : "—"}
                </td>
                <td className="px-3 py-2">{d.connection_status}</td>
                <td className="px-3 py-2">
                  {d.last_moisture != null ? `%${d.last_moisture}` : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AdminShell>
  );
}
