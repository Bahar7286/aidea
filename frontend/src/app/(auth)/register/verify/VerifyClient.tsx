"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { AuthSplitLayout } from "@/components/auth/AuthSplitLayout";
import { AuthStepper } from "@/components/auth/AuthStepper";
import { OtpInputs } from "@/components/auth/OtpInputs";
import { api, setSession } from "@/lib/api";

export default function VerifyClient() {
  const router = useRouter();
  const params = useSearchParams();
  const email = params.get("email") || "";
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [demoCode, setDemoCode] = useState<string | null>(null);
  const [seconds, setSeconds] = useState(90);

  useEffect(() => {
    const stored = sessionStorage.getItem("agritwin_demo_code");
    if (stored) setDemoCode(stored);
  }, []);

  useEffect(() => {
    if (seconds <= 0) return;
    const t = setTimeout(() => setSeconds((s) => s - 1), 1000);
    return () => clearTimeout(t);
  }, [seconds]);

  const timerLabel = useMemo(() => {
    const m = String(Math.floor(seconds / 60)).padStart(2, "0");
    const s = String(seconds % 60).padStart(2, "0");
    return `${m}:${s}`;
  }, [seconds]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!email) {
      setError("E-posta eksik. Kayıt adımına dönün.");
      return;
    }
    if (code.length !== 6) {
      setError("6 haneli doğrulama kodunu girin.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await api.verify({ email, code });
      setSession(data.access_token, data.user);
      sessionStorage.removeItem("agritwin_demo_code");
      router.push("/register/role");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Doğrulama başarısız.");
    } finally {
      setLoading(false);
    }
  }

  async function resend() {
    if (!email || seconds > 0) return;
    setError("");
    try {
      const res = await api.resendCode({ email });
      if (res.demo_code) {
        setDemoCode(res.demo_code);
        sessionStorage.setItem("agritwin_demo_code", res.demo_code);
      }
      setSeconds(90);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kod gönderilemedi.");
    }
  }

  return (
    <AuthSplitLayout
      panelTone="verify"
      panelTitle="Hesabınızı güvence altına alın."
      panelSubtitle="Doğrulama kodu ile e-posta adresinizi onaylayın."
    >
      <AuthStepper current={2} />
      <div className="space-y-5">
        <div>
          <h1 className="text-2xl font-bold text-[var(--auth-ink)]">Doğrulama Kodu</h1>
          <p className="mt-1 text-sm text-[var(--auth-muted)]">Kod şu adrese gönderildi:</p>
          <div className="mt-2 flex items-center justify-between rounded-xl border border-[var(--auth-forest)]/30 bg-[#f3faf5] px-3 py-2 text-sm">
            <span className="font-medium text-[var(--auth-ink)]">{email || "—"}</span>
            <Link href="/register" className="text-[var(--auth-accent)] hover:underline">
              Değiştir
            </Link>
          </div>
        </div>

        {demoCode && (
          <p className="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-900">
            MVP demo kodu: <strong>{demoCode}</strong> (gerçek SMS/e-posta yok)
          </p>
        )}

        <form className="space-y-4" onSubmit={onSubmit}>
          <OtpInputs value={code} onChange={setCode} />

          <p className="text-center text-sm text-[var(--auth-muted)]">
            Kodu almadınız mı?{" "}
            {seconds > 0 ? (
              <span>{timerLabel} sonra yeniden gönder</span>
            ) : (
              <button
                type="button"
                className="font-semibold text-[var(--auth-forest)]"
                onClick={resend}
              >
                Yeniden gönder
              </button>
            )}
          </p>

          <div className="rounded-lg bg-[#eef7f0] px-3 py-2 text-xs text-[var(--auth-forest)]">
            Bu adım hesabınızın güvenliği içindir. Kodu kimseyle paylaşmayın.
          </div>

          {error && (
            <p className="text-sm text-[var(--risk-critical)]" role="alert">
              {error}
            </p>
          )}

          <div className="flex items-center justify-between gap-3">
            <Link href="/register" className="btn btn-ghost">
              ← Geri
            </Link>
            <button className="btn btn-primary flex-1" disabled={loading}>
              {loading ? "Doğrulanıyor..." : "Doğrula ve Devam Et"}
            </button>
          </div>
        </form>
      </div>
    </AuthSplitLayout>
  );
}
