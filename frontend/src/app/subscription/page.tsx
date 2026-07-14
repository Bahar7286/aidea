"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app/AppShell";
import { api, setStoredUser, getStoredUser } from "@/lib/api";

type Plan = {
  id: string;
  name: string;
  price_try: number;
  price_label?: string;
  farms_limit: number;
  devices_limit: number | null;
  features: string[];
  current?: boolean;
};

export default function SubscriptionPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [current, setCurrent] = useState("free");
  const [note, setNote] = useState("");
  const [usage, setUsage] = useState({ farms: 0, devices: 0, ai: 0 });
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [busy, setBusy] = useState<string | null>(null);

  async function load() {
    const data = await api.billingPlans();
    setPlans(data.plans as Plan[]);
    setCurrent(data.current_plan);
    setNote(data.note);
    setUsage({
      farms: data.farms_used,
      devices: data.devices_used,
      ai: data.ai_queries_used,
    });
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function selectPlan(planId: string) {
    setBusy(planId);
    setError("");
    setOk("");
    try {
      const user = await api.selectBillingPlan(planId);
      const stored = getStoredUser();
      if (stored) {
        setStoredUser({ ...stored, subscription_plan: user.subscription_plan });
      }
      setOk(
        planId === "pro"
          ? "Pro (demo) planı seçildi — ödeme alınmaz."
          : "Ücretsiz plan aktif.",
      );
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Plan seçilemedi");
    } finally {
      setBusy(null);
    }
  }

  return (
    <AppShell title="Abonelik planları">
      <div className="mb-4">
        <Link href="/dashboard" className="text-sm text-[var(--auth-forest)] hover:underline">
          ← Genel bakış
        </Link>
      </div>

      <p className="mb-4 text-sm text-[var(--auth-muted)]">
        MVP demo abonelik: gerçek ödeme yoktur. Plan seçimi hesabınızda saklanır ve
        soft limit gösterimi için kullanılır.
      </p>

      <div className="mb-6 grid gap-3 sm:grid-cols-3">
        <div className="app-surface p-4">
          <p className="text-xs text-[var(--auth-muted)]">Arazi kullanımı</p>
          <p className="text-lg font-bold">{usage.farms}</p>
        </div>
        <div className="app-surface p-4">
          <p className="text-xs text-[var(--auth-muted)]">Cihaz kullanımı</p>
          <p className="text-lg font-bold">{usage.devices}</p>
        </div>
        <div className="app-surface p-4">
          <p className="text-xs text-[var(--auth-muted)]">AI sorguları</p>
          <p className="text-lg font-bold">{usage.ai}</p>
        </div>
      </div>

      {error && <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>}
      {ok && (
        <p className="mb-3 rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
          {ok}
        </p>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        {plans.map((p) => {
          const active = p.id === current || p.current;
          return (
            <div
              key={p.id}
              className={`app-surface space-y-3 p-5 ${
                active ? "ring-2 ring-[var(--auth-forest)]" : ""
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h2 className="text-lg font-bold">{p.name}</h2>
                  <p className="text-sm text-[var(--auth-muted)]">
                    {p.price_label ||
                      (p.price_try === 0 ? "0 ₺ / ay" : `${p.price_try} ₺ / ay`)}
                  </p>
                </div>
                {active && (
                  <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
                    Aktif
                  </span>
                )}
              </div>
              <ul className="space-y-1.5 text-sm text-[var(--auth-muted)]">
                <li>
                  · Arazi limiti:{" "}
                  <strong className="text-[var(--auth-ink)]">{p.farms_limit}</strong>
                </li>
                <li>
                  · Cihaz limiti:{" "}
                  <strong className="text-[var(--auth-ink)]">
                    {p.devices_limit ?? "sınırsız"}
                  </strong>
                </li>
                {(p.features || []).map((f) => (
                  <li key={f}>· {f}</li>
                ))}
              </ul>
              <button
                type="button"
                className={`btn w-full ${active ? "btn-secondary" : "btn-primary"}`}
                disabled={active || busy === p.id}
                onClick={() => selectPlan(p.id)}
              >
                {active
                  ? "Mevcut plan"
                  : busy === p.id
                    ? "Kaydediliyor…"
                    : "Bu planı seç"}
              </button>
            </div>
          );
        })}
      </div>

      {note && (
        <p className="mt-6 text-xs text-[var(--auth-muted)]">{note}</p>
      )}
    </AppShell>
  );
}
