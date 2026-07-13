"use client";

/** Small source label — never claim simulation as real sensors. */
export function SourceBadge({
  source,
  className = "",
}: {
  source?: string | null;
  className?: string;
}) {
  const raw = (source || "unknown").toLowerCase();
  const isSim = raw === "simulation" || raw.includes("simül");
  const isTest = raw === "test_dataset" || raw.includes("test");
  const isLab = raw.includes("lab");
  const label = isSim
    ? "Simülasyon"
    : isTest
      ? "Test veri seti"
      : isLab
        ? "Laboratuvar"
        : raw === "manual"
          ? "Manuel"
          : raw === "iot"
            ? "IoT"
            : source || "Kaynak";

  const tone = isSim
    ? "bg-amber-100 text-amber-900"
    : isTest
      ? "bg-sky-100 text-sky-900"
      : isLab
        ? "bg-violet-100 text-violet-900"
        : "bg-emerald-100 text-emerald-900";

  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-bold ${tone} ${className}`}
    >
      {label}
    </span>
  );
}
