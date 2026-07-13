/** Chronological moisture / sensor chart via Recharts. */
"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function HistoryChart({
  values,
  labels,
  label,
  unit = "",
}: {
  values: Array<number | null | undefined>;
  labels?: Array<string | null | undefined>;
  label: string;
  unit?: string;
}) {
  const data = values
    .map((v, i) =>
      typeof v === "number"
        ? {
            i,
            value: v,
            tick: labels?.[i] ?? String(i + 1),
          }
        : null,
    )
    .filter(Boolean) as Array<{ i: number; value: number; tick: string }>;

  if (data.length < 2) {
    return (
      <div className="flex h-56 items-center justify-center rounded-2xl border border-dashed border-[var(--auth-border)] bg-white text-sm text-[var(--auth-muted)]">
        Grafik için en az 2 ölçüm gerekli
      </div>
    );
  }

  const known = data.map((d) => d.value);
  const min = Math.min(...known);
  const max = Math.max(...known);
  const avg = known.reduce((s, v) => s + v, 0) / known.length;

  return (
    <div className="app-surface p-4">
      <p className="mb-2 text-sm font-semibold">
        {label} {unit && <span className="text-[var(--auth-muted)]">({unit})</span>}
      </p>
      <div className="h-52 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#d8e2d6" />
            <XAxis
              dataKey="tick"
              tick={{ fontSize: 10, fill: "#6b7c6e" }}
              interval="preserveStartEnd"
              minTickGap={28}
            />
            <YAxis
              domain={["auto", "auto"]}
              tick={{ fontSize: 10, fill: "#6b7c6e" }}
              width={36}
            />
            <Tooltip
              formatter={(value) => {
                const v = typeof value === "number" ? value.toFixed(1) : value ?? "";
                return [`${v}${unit ? ` ${unit}` : ""}`, label];
              }}
              contentStyle={{
                borderRadius: 12,
                borderColor: "#d8e2d6",
                fontSize: 12,
              }}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#1b4332"
              strokeWidth={2.5}
              dot={{ r: 3, fill: "#2d6a4f", strokeWidth: 0 }}
              activeDot={{ r: 5 }}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-2 grid grid-cols-3 gap-2 text-center text-xs text-[var(--auth-muted)]">
        <div>
          Ort <strong className="block text-[var(--auth-ink)]">{avg.toFixed(1)}</strong>
        </div>
        <div>
          Min <strong className="block text-[var(--auth-ink)]">{min.toFixed(1)}</strong>
        </div>
        <div>
          Max <strong className="block text-[var(--auth-ink)]">{max.toFixed(1)}</strong>
        </div>
      </div>
    </div>
  );
}
