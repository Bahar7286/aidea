"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app/AppShell";
import { FarmMaterialsPanel } from "@/components/app/FarmMaterialsPanel";
import { FarmSelector, setSelectedFarmId } from "@/components/app/FarmSelector";
import {
  api,
  clearSession,
  Farm,
  FarmHub,
  getStoredUser,
  setStoredUser,
  User,
} from "@/lib/api";

export default function HubPage() {
  const params = useParams();
  const router = useRouter();
  const farmId = Number(params.id);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [hub, setHub] = useState<FarmHub | null>(null);
  const [tab, setTab] = useState<"reports" | "alerts" | "settings">("reports");
  const [error, setError] = useState("");
  const [user, setUser] = useState<User | null>(null);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [profileMsg, setProfileMsg] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const stored = getStoredUser();
    setUser(stored);
    if (stored) {
      setName(stored.name || "");
      setPhone(stored.phone || "");
    }
  }, []);

  useEffect(() => {
    if (!farmId) return;
    setSelectedFarmId(farmId);
    Promise.all([api.getFarm(farmId), api.farmHub(farmId)])
      .then(([f, h]) => {
        setFarm(f);
        setHub(h);
        if (!getStoredUser()?.phone && h.settings.phone) {
          setPhone(String(h.settings.phone));
        }
      })
      .catch((err) => setError(err.message));
  }, [farmId]);

  function logout() {
    clearSession();
    router.push("/login");
  }

  async function saveProfile(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setProfileMsg("");
    try {
      const body: {
        name?: string;
        phone?: string;
        current_password?: string;
        new_password?: string;
      } = {
        name: name.trim() || undefined,
        phone: phone.trim() || undefined,
      };
      if (newPassword) {
        body.current_password = currentPassword;
        body.new_password = newPassword;
      }
      const updated = await api.updateMe(body);
      setStoredUser(updated);
      setUser(updated);
      setCurrentPassword("");
      setNewPassword("");
      setProfileMsg("Profil güncellendi.");
      const h = await api.farmHub(farmId);
      setHub(h);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Profil kaydedilemedi");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell title="Raporlar, Uyarılar ve Ayarlar" farmName={farm?.name}>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <FarmSelector farmId={farmId} suffixPath="/hub" />
      </div>

      {error && (
        <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>
      )}

      <div className="mb-4 flex gap-2 overflow-x-auto">
        {(
          [
            ["reports", "Raporlar"],
            ["alerts", "Uyarılar"],
            ["settings", "Ayarlar"],
          ] as const
        ).map(([k, label]) => (
          <button
            key={k}
            type="button"
            onClick={() => setTab(k)}
            className={`min-h-11 shrink-0 rounded-full px-3 py-1.5 text-xs font-semibold ${
              tab === k
                ? "bg-[var(--auth-forest)] text-white"
                : "bg-white ring-1 ring-[var(--auth-border)]"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "reports" && hub && (
        <div className="grid gap-6 lg:grid-cols-[1fr_260px]">
          <div className="space-y-3">
            {(hub.water_savings_liters != null || hub.water_used_liters != null) && (
              <div className="app-surface grid gap-3 p-4 sm:grid-cols-3">
                <div>
                  <p className="text-xs text-[var(--auth-muted)]">Kullanılan su</p>
                  <p className="text-lg font-bold">
                    {hub.water_used_liters != null
                      ? `${Math.round(hub.water_used_liters)} L`
                      : "—"}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-[var(--auth-muted)]">Tahmini tasarruf</p>
                  <p className="text-lg font-bold text-[var(--auth-forest)]">
                    {hub.water_savings_liters != null
                      ? `${Math.round(hub.water_savings_liters)} L`
                      : "—"}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-[var(--auth-muted)]">Oran</p>
                  <p className="text-lg font-bold">
                    {hub.water_savings_pct != null
                      ? `%${hub.water_savings_pct}`
                      : "—"}
                  </p>
                </div>
                {hub.water_usage_note && (
                  <p className="text-xs text-[var(--auth-muted)] sm:col-span-3">
                    {hub.water_usage_note}
                  </p>
                )}
              </div>
            )}
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {hub.reports.map((r) => (
                <div
                  key={r.key}
                  className={`app-surface p-4 ${!r.available ? "opacity-50" : ""}`}
                >
                  <p className="font-semibold">{r.title}</p>
                  <p className="mt-1 text-xs text-[var(--auth-muted)]">
                    {r.description}
                  </p>
                  <p className="mt-2 text-sm">
                    Kayıt: <strong>{r.record_count}</strong>
                    {!r.available && " · MVP dışı"}
                  </p>
                  {r.metric_value && (
                    <p className="mt-1 text-sm">
                      {r.metric_label || "Ölçüt"}:{" "}
                      <strong>{r.metric_value}</strong>
                    </p>
                  )}
                </div>
              ))}
            </div>
            <p className="text-xs text-[var(--auth-muted)]">{hub.note}</p>
          </div>
          <aside className="app-surface h-fit space-y-3 p-4 text-sm">
            <p className="font-semibold">Aktif uyarılar</p>
            <p className="text-xs text-[var(--auth-muted)]">
              Kritik {hub.alert_counts.critical || 0} · Yüksek{" "}
              {hub.alert_counts.high || 0} · Orta {hub.alert_counts.medium || 0}
            </p>
            <button
              type="button"
              className="btn btn-secondary min-h-11 w-full text-sm"
              onClick={() => setTab("alerts")}
            >
              Uyarılara git
            </button>
          </aside>
        </div>
      )}

      {tab === "alerts" && hub && (
        <ul className="space-y-3">
          {hub.alerts.map((a) => (
            <li key={a.code} className="app-surface p-4">
              <div className="flex items-start justify-between gap-2">
                <p className="font-semibold">{a.title}</p>
                <span
                  className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                    a.severity === "critical" || a.severity === "high"
                      ? "bg-red-100 text-red-800"
                      : "bg-amber-100 text-amber-900"
                  }`}
                >
                  {a.severity}
                </span>
              </div>
              <p className="mt-1 text-sm text-[var(--auth-muted)]">{a.message}</p>
            </li>
          ))}
          {hub.alerts.length === 0 && (
            <li className="rounded-2xl border border-dashed border-[var(--auth-border)] p-8 text-center text-sm text-[var(--auth-muted)]">
              Aktif uyarı yok.
            </li>
          )}
        </ul>
      )}

      {tab === "settings" && hub && (
        <div className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-2">
          <form className="app-surface space-y-3 p-4" onSubmit={saveProfile}>
            <p className="font-semibold">Profil</p>
            <label className="block text-sm">
              <span className="text-[var(--auth-muted)]">Ad</span>
              <input
                className="input mt-1 min-h-11"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                minLength={2}
              />
            </label>
            <label className="block text-sm">
              <span className="text-[var(--auth-muted)]">Telefon</span>
              <input
                className="input mt-1 min-h-11"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+90…"
              />
            </label>
            <p className="text-xs text-[var(--auth-muted)]">
              E-posta: {user?.email || hub.settings.email} (değiştirilemez)
            </p>
            <p className="text-xs text-[var(--auth-muted)]">
              Rol: {user?.role || hub.settings.user_role}
            </p>
            <div className="border-t border-[var(--auth-border)] pt-3">
              <p className="mb-2 text-sm font-semibold">Şifre değiştir</p>
              <label className="block text-sm">
                <span className="text-[var(--auth-muted)]">Mevcut şifre</span>
                <input
                  type="password"
                  className="input mt-1 min-h-11"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  autoComplete="current-password"
                />
              </label>
              <label className="mt-2 block text-sm">
                <span className="text-[var(--auth-muted)]">Yeni şifre</span>
                <input
                  type="password"
                  className="input mt-1 min-h-11"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  minLength={8}
                  autoComplete="new-password"
                />
              </label>
            </div>
            {profileMsg && (
              <p className="text-sm text-[var(--auth-forest)]">{profileMsg}</p>
            )}
            <div className="flex flex-wrap gap-2">
              <button
                type="submit"
                className="btn btn-primary min-h-11 text-sm"
                disabled={busy}
              >
                {busy ? "Kaydediliyor…" : "Kaydet"}
              </button>
              <button
                type="button"
                className="btn btn-secondary min-h-11 text-sm"
                onClick={logout}
              >
                Çıkış yap
              </button>
            </div>
          </form>
          <div className="app-surface space-y-3 p-4">
            <p className="font-semibold">Sistem</p>
            <ul className="space-y-2 text-sm text-[var(--auth-muted)]">
              <li>
                Otomasyon min. güven: %
                {String(hub.settings.min_confidence_automation)}
              </li>
              <li>
                Kritik nem eşiği: %
                {String(hub.settings.critical_moisture_pct)}
              </li>
              <li>Sulama: yalnızca sanal (onay zorunlu)</li>
            </ul>
            <Link
              href="/subscription"
              className="btn btn-primary min-h-11 w-full text-sm"
            >
              Abonelik planları
            </Link>
            <Link href={`/farms/${farmId}`} className="btn btn-ghost min-h-11 text-sm">
              Arazi detayına dön
            </Link>
          </div>
          </div>
          <FarmMaterialsPanel
            farmId={farmId}
            initialUses={farm?.material_uses}
            onSaved={setFarm}
          />
        </div>
      )}
    </AppShell>
  );
}
