"use client";

import { FormEvent, useEffect, useState } from "react";
import { AdminShell } from "@/components/admin/AdminShell";
import { api, SupportTicket } from "@/lib/api";

export default function AdminSupportPage() {
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [filter, setFilter] = useState("all");
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function load(status = filter) {
    const list = await api.adminTickets(
      status === "all" ? undefined : status,
    );
    setTickets(list);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  async function create(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.createTicket({
        subject,
        description: description || undefined,
        priority: "medium",
      });
      setSubject("");
      setDescription("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Oluşturulamadı");
    } finally {
      setBusy(false);
    }
  }

  async function setStatus(id: number, status: string) {
    try {
      await api.adminUpdateTicket(id, { status });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Güncellenemedi");
    }
  }

  return (
    <AdminShell title="Destek Talepleri">
      {error && <p className="mb-3 text-sm text-red-700">{error}</p>}

      <form onSubmit={create} className="app-surface mb-4 space-y-2 p-4">
        <p className="text-sm font-semibold">Yeni talep</p>
        <input
          className="input"
          placeholder="Konu"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          required
        />
        <textarea
          className="input min-h-[70px]"
          placeholder="Açıklama"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <button type="submit" className="btn btn-primary text-sm" disabled={busy}>
          Oluştur
        </button>
      </form>

      <div className="mb-4 flex flex-wrap gap-2">
        {(["all", "open", "pending", "resolved", "closed"] as const).map(
          (f) => (
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
          ),
        )}
      </div>

      <ul className="space-y-3">
        {tickets.map((t) => (
          <li key={t.id} className="app-surface p-4">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p className="text-xs text-[var(--auth-muted)]">{t.ticket_no}</p>
                <p className="font-semibold">{t.subject}</p>
                <p className="text-xs text-[var(--auth-muted)]">
                  {t.description || "—"}
                </p>
              </div>
              <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-900">
                {t.priority} · {t.status}
              </span>
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {["open", "pending", "resolved", "closed"].map((s) => (
                <button
                  key={s}
                  type="button"
                  className="btn btn-ghost text-xs"
                  onClick={() => setStatus(t.id, s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </li>
        ))}
        {tickets.length === 0 && (
          <li className="rounded-2xl border border-dashed border-[var(--auth-border)] p-8 text-center text-sm text-[var(--auth-muted)]">
            Talep yok
          </li>
        )}
      </ul>
    </AdminShell>
  );
}
