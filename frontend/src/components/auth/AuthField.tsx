"use client";

import { InputHTMLAttributes, useState } from "react";

type Props = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  icon?: "user" | "lock" | "mail" | "phone";
};

function FieldIcon({ name }: { name: NonNullable<Props["icon"]> }) {
  const common = "h-4 w-4 text-[var(--auth-muted)]";
  if (name === "lock") {
    return (
      <svg className={common} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="5" y="11" width="14" height="10" rx="2" />
        <path d="M8 11V8a4 4 0 0 1 8 0v3" />
      </svg>
    );
  }
  if (name === "mail") {
    return (
      <svg className={common} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="3" y="5" width="18" height="14" rx="2" />
        <path d="m3 7 9 7 9-7" />
      </svg>
    );
  }
  if (name === "phone") {
    return (
      <svg className={common} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M6 3h4l2 5-3 2a12 12 0 0 0 5 5l2-3 5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 4 5a2 2 0 0 1 2-2Z" />
      </svg>
    );
  }
  return (
    <svg className={common} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="8" r="4" />
      <path d="M4 20a8 8 0 0 1 16 0" />
    </svg>
  );
}

export function AuthField({ label, icon, type = "text", className = "", ...rest }: Props) {
  const [show, setShow] = useState(false);
  const isPassword = type === "password";
  return (
    <div>
      <label className="label text-[var(--auth-ink)]" htmlFor={rest.id}>
        {label}
      </label>
      <div className="relative">
        {icon && (
          <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2">
            <FieldIcon name={icon} />
          </span>
        )}
        <input
          {...rest}
          type={isPassword && show ? "text" : type}
          className={`input auth-input ${icon ? "pl-10" : ""} ${isPassword ? "pr-12" : ""} ${className}`}
        />
        {isPassword && (
          <button
            type="button"
            className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-medium text-[var(--auth-muted)]"
            onClick={() => setShow((v) => !v)}
            aria-label={show ? "Şifreyi gizle" : "Şifreyi göster"}
          >
            {show ? "Gizle" : "Göster"}
          </button>
        )}
      </div>
    </div>
  );
}

export function PasswordRules({ password }: { password: string }) {
  const rules = [
    { ok: password.length >= 8, label: "8+ karakter" },
    { ok: /[A-Z]/.test(password), label: "1 büyük harf" },
    { ok: /[a-z]/.test(password), label: "1 küçük harf" },
    { ok: /\d/.test(password), label: "1 rakam" },
  ];
  return (
    <ul className="mt-2 grid grid-cols-2 gap-1 text-xs">
      {rules.map((r) => (
        <li
          key={r.label}
          className={r.ok ? "text-[var(--auth-forest)]" : "text-[var(--auth-muted)]"}
        >
          {r.ok ? "✓" : "○"} {r.label}
        </li>
      ))}
    </ul>
  );
}
