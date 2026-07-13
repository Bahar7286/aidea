"use client";

import {
  ClipboardEvent,
  KeyboardEvent,
  useRef,
} from "react";

type Props = {
  value: string;
  onChange: (code: string) => void;
};

export function OtpInputs({ value, onChange }: Props) {
  const digits = value.padEnd(6, " ").slice(0, 6).split("");
  const refs = useRef<Array<HTMLInputElement | null>>([]);

  function setDigit(index: number, char: string) {
    const next = digits.map((d, i) => (i === index ? char : d === " " ? "" : d));
    const code = next.join("").replace(/\s/g, "").slice(0, 6);
    onChange(code);
  }

  function onKeyDown(index: number, e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Backspace" && !digits[index]?.trim() && index > 0) {
      refs.current[index - 1]?.focus();
    }
  }

  function onPaste(e: ClipboardEvent<HTMLInputElement>) {
    e.preventDefault();
    const text = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    onChange(text);
    const focusAt = Math.min(text.length, 5);
    refs.current[focusAt]?.focus();
  }

  return (
    <div className="flex justify-between gap-2">
      {Array.from({ length: 6 }).map((_, i) => (
        <input
          key={i}
          ref={(el) => {
            refs.current[i] = el;
          }}
          inputMode="numeric"
          maxLength={1}
          className="auth-otp"
          value={digits[i]?.trim() || ""}
          onChange={(e) => {
            const char = e.target.value.replace(/\D/g, "").slice(-1);
            setDigit(i, char);
            if (char && i < 5) refs.current[i + 1]?.focus();
          }}
          onKeyDown={(e) => onKeyDown(i, e)}
          onPaste={onPaste}
          aria-label={`Kod ${i + 1}`}
        />
      ))}
    </div>
  );
}
