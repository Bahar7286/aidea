type Zone = { name: string; moisture?: number | null; tone?: "ok" | "warn" | "risk" };

export function SchematicMap({
  zones,
  label = "Sınırlı dijital ikiz",
}: {
  zones: Zone[];
  label?: string;
}) {
  const items =
    zones.length > 0
      ? zones
      : [
          { name: "Bölge A", moisture: null },
          { name: "Bölge B", moisture: null },
          { name: "Bölge C", moisture: null },
        ];

  const color = (z: Zone) => {
    if (z.moisture == null) return "bg-slate-300/80";
    if (z.moisture < 25) return "bg-orange-400/90";
    if (z.moisture < 32) return "bg-amber-300/90";
    return "bg-emerald-500/85";
  };

  return (
    <div className="overflow-hidden rounded-2xl border border-[var(--auth-border)] bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-[var(--auth-border)] px-4 py-2.5">
        <p className="text-sm font-semibold">Arazi haritası</p>
        <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-[var(--auth-forest)]">
          {label}
        </span>
      </div>
      <div className="relative aspect-[4/3] bg-gradient-to-br from-[#3d5a40] via-[#5a7a4a] to-[#8fa86a] p-4">
        <div className="grid h-full grid-cols-3 gap-2">
          {items.slice(0, 3).map((z) => (
            <div
              key={z.name}
              className={`flex flex-col justify-between rounded-xl border border-white/30 p-2 text-white shadow-inner ${color(z)}`}
            >
              <span className="text-[11px] font-semibold drop-shadow">{z.name}</span>
              <span className="text-lg font-bold drop-shadow">
                {z.moisture != null ? `%${z.moisture}` : "—"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
