type Zone = { name: string; moisture?: number | null; tone?: "ok" | "warn" | "risk" };

/** areaDa: Turkish dekar (1 ha ≈ 10 da). Scales schematic plot footprint. */
export function SchematicMap({
  zones,
  label = "Sınırlı dijital ikiz",
  areaDa,
}: {
  zones: Zone[];
  label?: string;
  areaDa?: number | null;
}) {
  const items =
    zones.length > 0
      ? zones
      : [
          { name: "Bölge A", moisture: null },
          { name: "Bölge B", moisture: null },
          { name: "Bölge C", moisture: null },
        ];

  const area = Math.max(0.5, areaDa ?? 2);
  // Relative to ~2 da baseline; clamp so UI stays usable
  const scale = Math.min(1.35, Math.max(0.55, Math.sqrt(area / 2)));
  const cols = items.length >= 3 ? 3 : Math.max(1, items.length);
  const aspect = area >= 8 ? "aspect-[16/9]" : area >= 4 ? "aspect-[5/3]" : "aspect-[4/3]";
  const haLabel = (area / 10).toFixed(area >= 10 ? 1 : 2);

  const color = (z: Zone) => {
    if (z.moisture == null) return "#94a3b8";
    if (z.moisture < 25) return "#fb923c";
    if (z.moisture < 32) return "#fbbf24";
    return "#22c55e";
  };

  const slicePath = (i: number, n: number) => {
    // Irregular plot polygon that grows with area (viewBox 0..100)
    const pad = 8 / scale;
    const w = 100 - pad * 2;
    const h = 100 - pad * 2;
    const sliceW = w / n;
    const x0 = pad + i * sliceW;
    const x1 = x0 + sliceW;
    const topWiggle = (i % 2 === 0 ? 2 : -2) * scale;
    const bottomWiggle = (i % 2 === 0 ? -3 : 3) * scale;
    return `M ${x0 + 1} ${pad + topWiggle}
      L ${x1 - 1} ${pad - topWiggle * 0.5}
      L ${x1 + bottomWiggle * 0.3} ${pad + h + bottomWiggle}
      L ${x0 - bottomWiggle * 0.2} ${pad + h - bottomWiggle * 0.4}
      Z`;
  };

  return (
    <div className="overflow-hidden rounded-2xl border border-[var(--auth-border)] bg-white shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--auth-border)] px-4 py-2.5">
        <p className="text-sm font-semibold">Arazi haritası</p>
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-700">
            {area.toFixed(1)} da · ~{haLabel} ha
          </span>
          <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-[var(--auth-forest)]">
            {label}
          </span>
        </div>
      </div>
      <div
        className={`relative ${aspect} bg-gradient-to-br from-[#2d4a32] via-[#5a7a4a] to-[#8fa86a] p-3 sm:p-4`}
      >
        <div
          className="mx-auto h-full transition-transform duration-500 ease-out"
          style={{ width: `${Math.round(scale * 100)}%`, maxWidth: "100%" }}
        >
          <svg viewBox="0 0 100 100" className="h-full w-full drop-shadow-md" aria-hidden>
            {items.slice(0, cols).map((z, i) => (
              <g key={z.name}>
                <path
                  d={slicePath(i, cols)}
                  fill={color(z)}
                  fillOpacity={0.88}
                  stroke="rgba(255,255,255,0.55)"
                  strokeWidth={0.6}
                />
                <text
                  x={8 / scale + ((100 - 16 / scale) / cols) * (i + 0.5)}
                  y={28}
                  textAnchor="middle"
                  className="fill-white"
                  style={{ fontSize: 4.2, fontWeight: 700 }}
                >
                  {z.name}
                </text>
                <text
                  x={8 / scale + ((100 - 16 / scale) / cols) * (i + 0.5)}
                  y={42}
                  textAnchor="middle"
                  className="fill-white"
                  style={{ fontSize: 6, fontWeight: 800 }}
                >
                  {z.moisture != null ? `%${z.moisture}` : "—"}
                </text>
              </g>
            ))}
          </svg>
        </div>
      </div>
    </div>
  );
}
