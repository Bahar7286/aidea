"use client";

import { FormEvent, useEffect, useState } from "react";
import { AdminShell } from "@/components/admin/AdminShell";
import { api, AdminSettings } from "@/lib/api";

export default function AdminSettingsPage() {
  const [data, setData] = useState<AdminSettings | null>(null);
  const [form, setForm] = useState<Record<string, string>>({});
  const [error, setError] = useState("");
  const [saved, setSaved] = useState("");

  useEffect(() => {
    api
      .adminSettings()
      .then((s) => {
        setData(s);
        setForm(s.settings);
      })
      .catch((err) => setError(err.message));
  }, []);

  async function onSave(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSaved("");
    try {
      const res = await api.adminUpdateSettings(form);
      setData(res);
      setForm(res.settings);
      setSaved("Ayarlar kaydedildi.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kayıt başarısız");
    }
  }

  return (
    <AdminShell title="Sistem Ayarları ve Entegrasyonlar">
      {error && <p className="mb-3 text-sm text-red-700">{error}</p>}
      {saved && <p className="mb-3 text-sm text-emerald-700">{saved}</p>}

      <form onSubmit={onSave} className="grid gap-4 lg:grid-cols-2">
        <div className="app-surface space-y-3 p-4">
          <p className="text-sm font-semibold">Genel</p>
          {[
            ["system_name", "Sistem adı"],
            ["language", "Dil"],
            ["timezone", "Saat dilimi"],
            ["currency", "Para birimi"],
            ["critical_moisture_pct", "Kritik nem %"],
            ["session_timeout_min", "Oturum (dk)"],
          ].map(([key, label]) => (
            <div key={key}>
              <label className="label" htmlFor={key}>
                {label}
              </label>
              <input
                id={key}
                className="input"
                value={form[key] ?? ""}
                onChange={(e) =>
                  setForm((prev) => ({ ...prev, [key]: e.target.value }))
                }
              />
            </div>
          ))}
          {[
            ["maintenance_mode", "Bakım modu"],
            ["auto_backup", "Otomatik yedek"],
            ["notify_email", "E-posta bildirimi"],
            ["notify_irrigation", "Sulama bildirimi"],
          ].map(([key, label]) => (
            <label key={key} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={form[key] === "true"}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    [key]: e.target.checked ? "true" : "false",
                  }))
                }
              />
              {label}
            </label>
          ))}
          <button type="submit" className="btn btn-primary">
            Kaydet
          </button>
        </div>

        <div className="app-surface space-y-3 p-4">
          <p className="text-sm font-semibold">Entegrasyonlar</p>
          <ul className="space-y-2 text-sm">
            {(data?.integrations || []).map((i) => (
              <li
                key={i.name}
                className="flex items-center justify-between border-b border-[var(--auth-border)] pb-2 last:border-0"
              >
                <span>{i.name}</span>
                <span
                  className={`text-xs font-bold ${
                    i.connected ? "text-emerald-700" : "text-[var(--auth-muted)]"
                  }`}
                >
                  {i.connected ? "Bağlı (sim)" : i.status}
                </span>
              </li>
            ))}
          </ul>
          <p className="text-[11px] text-[var(--auth-muted)]">{data?.note}</p>
        </div>
      </form>
    </AdminShell>
  );
}
