/** 72h moisture forecast chart (now / 24h / 48h / 72h) via Recharts. */
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

const AXIS = ["şimdi", "24s", "48s", "72s"] as const;

export function MoistureSparkline({
  points,
}: {
  points: Array<number | null | undefined>;
}) {
  const data = AXIS.map((name, i) => {
    const v = points[i];
    return typeof v === "number" ? { name, value: v } : { name, value: null as number | null };
  }).filter((d) => d.value != null) as Array<{ name: string; value: number }>;

  if (data.length === 0) {
    return (
      <div className="flex h-40 items-center justify-center rounded-2xl border border-dashed border-[var(--auth-border)] bg-white text-sm text-[var(--auth-muted)]">
        Tahmin verisi yok — önce analiz çalıştırın
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-[var(--auth-border)] bg-white p-4 shadow-sm">
      <p className="mb-2 text-sm font-semibold">72 saatlik nem tahmini</p>
      <div className="h-36 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#d8e2d6" />
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#6b7c6e" }} />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 10, fill: "#6b7c6e" }}
              width={32}
              unit="%"
            />
            <Tooltip
              formatter={(value: number | string) => [
                `${typeof value === "number" ? value.toFixed(1) : value}%`,
                "Nem",
              ]}
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
              strokeWidth={3}
              dot={{ r: 4, fill: "#2d6a4f", strokeWidth: 0 }}
              activeDot={{ r: 6 }}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
