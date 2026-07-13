const STEPS = [
  { id: 1, label: "Hesap Bilgileri" },
  { id: 2, label: "Doğrulama" },
  { id: 3, label: "Kullanıcı Türü" },
  { id: 4, label: "Tamamlandı" },
] as const;

export function AuthStepper({ current }: { current: 1 | 2 | 3 | 4 }) {
  return (
    <ol className="mb-8 grid grid-cols-4 gap-2">
      {STEPS.map((step) => {
        const done = step.id < current;
        const active = step.id === current;
        return (
          <li key={step.id} className="flex flex-col items-center gap-1.5 text-center">
            <span
              className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${
                active || done
                  ? "bg-[var(--auth-forest)] text-white"
                  : "bg-[var(--auth-border)] text-[var(--auth-muted)]"
              }`}
            >
              {done ? "✓" : step.id}
            </span>
            <span
              className={`hidden text-[10px] leading-tight sm:block ${
                active ? "font-semibold text-[var(--auth-forest)]" : "text-[var(--auth-muted)]"
              }`}
            >
              {step.label}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
