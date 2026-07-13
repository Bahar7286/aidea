"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "@/components/admin/AdminShell";
import { KpiCard } from "@/components/app/KpiCard";
import { api, AdminUser } from "@/lib/api";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [filter, setFilter] = useState("all");
  const [q, setQ] = useState("");
  const [error, setError] = useState("");

  async function load(status = filter, query = q) {
    const list = await api.adminUsers({
      status: status === "all" ? undefined : status,
      q: query.trim() || undefined,
    });
    setUsers(list);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  async function toggleActive(u: AdminUser) {
    try {
      await api.adminUpdateUser(u.id, { is_active: !u.is_active });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Güncellenemedi");
    }
  }

  async function setRole(u: AdminUser, role: string) {
    try {
      await api.adminUpdateUser(u.id, { role });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Rol güncellenemedi");
    }
  }

  const active = users.filter((u) => u.is_active).length;
  const admins = users.filter((u) =>
    ["admin", "super_admin"].includes(u.role),
  ).length;

  return (
    <AdminShell title="Kullanıcı Yönetimi">
      {error && <p className="mb-3 text-sm text-red-700">{error}</p>}
      <div className="mb-4 grid gap-3 sm:grid-cols-4">
        <KpiCard label="Toplam" value={String(users.length)} />
        <KpiCard label="Aktif" value={String(active)} tone="ok" />
        <KpiCard label="Admin" value={String(admins)} />
        <KpiCard
          label="Doğrulanmamış"
          value={String(users.filter((u) => !u.email_verified).length)}
          tone="warn"
        />
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {(["all", "active", "passive", "pending"] as const).map((f) => (
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
        <form
          className="ml-auto flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            load().catch((err) => setError(err.message));
          }}
        >
          <input
            className="input text-sm"
            placeholder="Ara"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <button type="submit" className="btn btn-secondary text-sm">
            Filtre
          </button>
        </form>
      </div>

      <ul className="space-y-3 lg:hidden">
        {users.map((u) => (
          <li key={u.id} className="app-surface p-4 text-sm">
            <p className="font-semibold">{u.name}</p>
            <p className="text-xs text-[var(--auth-muted)]">{u.email}</p>
            <p className="mt-1 text-xs">
              {u.role} · {u.farm_count} arazi ·{" "}
              {u.is_active ? "aktif" : "pasif"}
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              <select
                className="input py-1 text-xs"
                value={u.role}
                onChange={(e) => setRole(u, e.target.value)}
              >
                {[
                  "farmer",
                  "agronomist",
                  "consultant",
                  "operator",
                  "admin",
                ].map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
              <button
                type="button"
                className="btn btn-secondary text-xs"
                onClick={() => toggleActive(u)}
              >
                {u.is_active ? "Pasifleştir" : "Aktifleştir"}
              </button>
            </div>
          </li>
        ))}
      </ul>

      <div className="app-surface hidden overflow-x-auto lg:block">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="text-xs text-[var(--auth-muted)]">
            <tr>
              <th className="px-3 py-2">Kullanıcı</th>
              <th className="px-3 py-2">Rol</th>
              <th className="px-3 py-2">Arazi</th>
              <th className="px-3 py-2">Durum</th>
              <th className="px-3 py-2">Son giriş</th>
              <th className="px-3 py-2" />
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-t border-[var(--auth-border)]">
                <td className="px-3 py-2">
                  <p className="font-medium">{u.name}</p>
                  <p className="text-xs text-[var(--auth-muted)]">{u.email}</p>
                </td>
                <td className="px-3 py-2">
                  <select
                    className="input py-1 text-xs"
                    value={u.role}
                    onChange={(e) => setRole(u, e.target.value)}
                  >
                    {[
                      "farmer",
                      "agronomist",
                      "consultant",
                      "operator",
                      "admin",
                    ].map((r) => (
                      <option key={r} value={r}>
                        {r}
                      </option>
                    ))}
                  </select>
                </td>
                <td className="px-3 py-2">{u.farm_count}</td>
                <td className="px-3 py-2">
                  {u.is_active ? "Aktif" : "Pasif"}
                </td>
                <td className="px-3 py-2 text-xs">
                  {u.last_login_at
                    ? new Date(u.last_login_at).toLocaleString("tr-TR")
                    : "—"}
                </td>
                <td className="px-3 py-2">
                  <button
                    type="button"
                    className="text-xs text-[var(--auth-forest)] hover:underline"
                    onClick={() => toggleActive(u)}
                  >
                    {u.is_active ? "Pasifleştir" : "Aktifleştir"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AdminShell>
  );
}
