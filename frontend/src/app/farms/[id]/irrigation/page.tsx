"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app/AppShell";
import { FarmSelector, setSelectedFarmId } from "@/components/app/FarmSelector";
import { api, Farm, IrrigationEvent } from "@/lib/api";

function formatCountdown(totalSeconds: number | null | undefined) {
  if (totalSeconds == null || Number.isNaN(totalSeconds)) return "—";
  const s = Math.max(0, Math.floor(totalSeconds));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${r.toString().padStart(2, "0")}`;
}

export default function IrrigationPage() {
  const params = useParams();
  const farmId = Number(params.id);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [tab, setTab] = useState<"manual" | "plan">("manual");
  const [duration, setDuration] = useState(30);
  const [water, setWater] = useState(180);
  const [status, setStatus] = useState<{
    valve_status: string;
    pump_status?: string;
    running: IrrigationEvent | null;
    remaining_seconds?: number | null;
    planned_end?: string | null;
    current_moisture: number | null;
    confidence_score: number;
    automation_allowed: boolean;
    message: string;
  } | null>(null);
  const [remaining, setRemaining] = useState<number | null>(null);
  const [history, setHistory] = useState<IrrigationEvent[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);

  async function load() {
    const [f, st, hist] = await Promise.all([
      api.getFarm(farmId),
      api.irrigationStatus(farmId),
      api.irrigationHistory(farmId),
    ]);
    setFarm(f);
    setStatus(st);
    setRemaining(
      st.remaining_seconds != null ? Number(st.remaining_seconds) : null,
    );
    setHistory(hist);
  }

  useEffect(() => {
    if (!farmId) return;
    setSelectedFarmId(farmId);
    load().catch((err) => setError(err.message));
  }, [farmId]);

  useEffect(() => {
    if (!status?.running) {
      setRemaining(null);
      return;
    }
    const tick = window.setInterval(() => {
      setRemaining((prev) => {
        if (prev == null) return prev;
        return Math.max(0, prev - 1);
      });
    }, 1000);
    const poll = window.setInterval(() => {
      load().catch(() => undefined);
    }, 15000);
    return () => {
      window.clearInterval(tick);
      window.clearInterval(poll);
    };
  }, [status?.running?.id, farmId]);

  async function startSession() {
    setConfirmOpen(false);
    setBusy(true);
    setError("");
    try {
      await api.startIrrigation(farmId, duration, true);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Başlatılamadı");
    } finally {
      setBusy(false);
    }
  }

  async function stopSession() {
    setBusy(true);
    setError("");
    try {
      await api.stopIrrigation(farmId, status?.running?.id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Durdurulamadı");
    } finally {
      setBusy(false);
    }
  }

  async function instantComplete() {
    setConfirmOpen(false);
    setBusy(true);
    setError("");
    try {
      await api.startIrrigation(farmId, duration, false);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sulama başarısız");
    } finally {
      setBusy(false);
    }
  }

  const running = !!status?.running;

  return (
    <AppShell title="Sulama Kontrol ve Planlama" farmName={farm?.name}>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <FarmSelector farmId={farmId} suffixPath="/irrigation" />
        <Link href={`/farms/${farmId}/scenarios`} className="btn btn-ghost text-sm">
          Senaryo
        </Link>
        <Link href={`/farms/${farmId}/ai`} className="btn btn-ghost text-sm">
          AI
        </Link>
      </div>

      {error && (
        <p className="mb-3 text-sm text-[var(--risk-critical)]">{error}</p>
      )}

      <div className="mb-4 flex gap-2">
        {(
          [
            ["manual", "Manuel"],
            ["plan", "Planlama"],
          ] as const
        ).map(([k, label]) => (
          <button
            key={k}
            type="button"
            onClick={() => setTab(k)}
            className={`min-h-11 rounded-full px-3 py-1.5 text-xs font-semibold ${
              tab === k
                ? "bg-[var(--auth-forest)] text-white"
                : "bg-white ring-1 ring-[var(--auth-border)]"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "manual" ? (
        <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
          <div className="app-surface space-y-4 p-4 sm:p-6">
            <div className="flex flex-wrap items-center gap-4">
              <div
                className={`flex h-24 w-24 items-center justify-center rounded-full border-4 text-center text-xs font-bold ${
                  running
                    ? "border-emerald-500 text-emerald-800"
                    : "border-slate-300 text-slate-500"
                }`}
              >
                {running ? "Çalışıyor" : "Beklemede"}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold">
                  Vana: {status?.valve_status || "—"} · Pompa:{" "}
                  {status?.pump_status || status?.valve_status || "—"}
                </p>
                <p className="text-xs text-[var(--auth-muted)]">
                  {status?.message}
                </p>
                {running && (
                  <p className="mt-2 text-2xl font-bold tabular-nums text-[var(--auth-forest)]">
                    {formatCountdown(remaining)}
                    <span className="ml-2 text-xs font-medium text-[var(--auth-muted)]">
                      kalan (sanal)
                    </span>
                  </p>
                )}
                <p className="mt-1 text-sm">
                  Nem:{" "}
                  <strong>
                    {status?.current_moisture != null
                      ? `%${status.current_moisture}`
                      : "—"}
                  </strong>{" "}
                  · Güven: %{status?.confidence_score?.toFixed?.(0) ?? "—"}
                </p>
              </div>
            </div>

            <div>
              <label className="label">
                Süre: {duration} dk · Su ~{water} L
              </label>
              <input
                type="range"
                min={5}
                max={120}
                value={duration}
                disabled={running}
                onChange={(e) => {
                  const v = Number(e.target.value);
                  setDuration(v);
                  setWater(Math.round(v * 6));
                }}
                className="w-full"
              />
            </div>

            {!status?.automation_allowed && (
              <p className="rounded-xl bg-amber-50 px-3 py-2 text-xs text-amber-950">
                Otomasyon için AI sulama önerisi + güven ≥ %60 gerekir. Anlık sanal
                oturum yine onayla başlar.
              </p>
            )}

            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                className="btn btn-primary min-h-11"
                disabled={busy || running}
                onClick={() => setConfirmOpen(true)}
              >
                Sulamayı başlat
              </button>
              <button
                type="button"
                className="btn min-h-11 bg-red-600 text-white hover:bg-red-700"
                disabled={busy || !running}
                onClick={stopSession}
              >
                Sulamayı durdur
              </button>
              <Link
                href={`/farms/${farmId}/scenarios`}
                className="btn btn-secondary min-h-11 text-sm"
              >
                Detaylı kontrol
              </Link>
            </div>
          </div>

          <aside className="app-surface p-4">
            <p className="mb-2 text-sm font-semibold">Planlanan / geçmiş</p>
            <ul className="space-y-2 text-xs text-[var(--auth-muted)]">
              {history.slice(0, 8).map((h) => (
                <li
                  key={h.id}
                  className="border-b border-[var(--auth-border)] pb-2 last:border-0"
                >
                  <span className="font-medium text-[var(--auth-ink)]">
                    {h.status}
                  </span>{" "}
                  · {h.duration ?? "—"} dk · {h.water_amount ?? "—"} L
                  <br />
                  {new Date(h.start_time).toLocaleString("tr-TR")}
                </li>
              ))}
              {history.length === 0 && <li>Kayıt yok</li>}
            </ul>
          </aside>
        </div>
      ) : (
        <div className="app-surface space-y-3 p-4">
          <p className="text-sm font-semibold">Planlama (MVP)</p>
          <p className="text-sm text-[var(--auth-muted)]">
            Zamanlanmış sulama takvimi P2. Şimdilik geçmiş olaylar ve AI önerisi
            üzerinden manuel / sanal oturum kullanın.
          </p>
          <Link href={`/farms/${farmId}/ai`} className="btn btn-primary min-h-11 text-sm">
            AI önerisine git
          </Link>
        </div>
      )}

      {confirmOpen && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-4 sm:items-center">
          <div className="app-surface w-full max-w-md space-y-3 p-5">
            <p className="font-semibold">Sanal sulama onayı</p>
            <p className="text-sm text-[var(--auth-muted)]">
              Gerçek vana yok. Oturum açılırsa durdurana kadar “çalışıyor”
              kalır; anlık tamamla ise nem hemen güncellenir.
            </p>
            <div className="flex flex-col gap-2 sm:flex-row">
              <button
                type="button"
                className="btn btn-secondary min-h-11 flex-1"
                onClick={() => setConfirmOpen(false)}
              >
                Vazgeç
              </button>
              <button
                type="button"
                className="btn btn-secondary min-h-11 flex-1"
                disabled={busy}
                onClick={instantComplete}
              >
                Anlık tamamla
              </button>
              <button
                type="button"
                className="btn btn-primary min-h-11 flex-1"
                disabled={busy}
                onClick={startSession}
              >
                Oturum başlat
              </button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
