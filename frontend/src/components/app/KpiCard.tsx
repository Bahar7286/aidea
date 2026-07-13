type KpiCardProps = {
  label: string;
  value: string;
  hint?: string;
  tone?: "ok" | "warn" | "neutral";
};

export function KpiCard({ label, value, hint, tone = "neutral" }: KpiCardProps) {
  const toneClass =
    tone === "ok"
      ? "border-emerald-200 bg-emerald-50/60"
      : tone === "warn"
        ? "border-amber-200 bg-amber-50/70"
        : "border-[var(--auth-border)] bg-white";
  return (
    <div className={`rounded-2xl border p-4 shadow-sm ${toneClass}`}>
      <p className="text-xs font-medium text-[var(--auth-muted)]">{label}</p>
      <p className="mt-1 text-2xl font-bold tracking-tight">{value}</p>
      {hint && <p className="mt-1 text-xs text-[var(--auth-muted)]">{hint}</p>}
    </div>
  );
}
