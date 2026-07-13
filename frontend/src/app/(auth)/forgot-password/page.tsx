"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { AuthSplitLayout } from "@/components/auth/AuthSplitLayout";
import { AuthField, PasswordRules } from "@/components/auth/AuthField";
import { OtpInputs } from "@/components/auth/OtpInputs";
import { api } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [step, setStep] = useState<"request" | "reset">("request");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [demoCode, setDemoCode] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onRequest(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");
    const form = new FormData(e.currentTarget);
    const login = String(form.get("email"));
    try {
      const res = await api.forgotPassword({ email: login });
      setMessage(res.message);
      if (res.demo_code) setDemoCode(res.demo_code);
      if (res.email) {
        setEmail(res.email);
        setStep("reset");
      } else if (login.includes("@")) {
        setEmail(login.toLowerCase());
        setStep("reset");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "İstek başarısız.");
    } finally {
      setLoading(false);
    }
  }

  async function onReset(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const form = new FormData(e.currentTarget);
      const resetEmail = String(form.get("reset_email") || email);
      await api.resetPassword({
        email: resetEmail,
        code,
        new_password: password,
      });
      setMessage("Şifreniz güncellendi. Giriş sayfasına yönlendiriliyor...");
      window.location.href = "/login";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Şifre sıfırlanamadı.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthSplitLayout
      panelTone="forgot"
      panelTitle="Şifrenizi mi unuttunuz?"
      panelSubtitle="Doğrulama kodu ile güvenli şekilde yeni şifre belirleyin."
    >
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--auth-ink)]">
            Şifrenizi sıfırlayın
          </h1>
          <p className="mt-1 text-sm text-[var(--auth-muted)]">
            {step === "request"
              ? "Hesabınıza bağlı e-posta veya telefon ile kod alın."
              : "Kod ve yeni şifrenizi girin."}
          </p>
        </div>

        {step === "request" ? (
          <form className="space-y-4" onSubmit={onRequest}>
            <AuthField
              id="email"
              name="email"
              label="E-posta veya Telefon"
              icon="mail"
              placeholder="ornek@email.com veya 5XXXXXXXXX"
              required
            />
            {error && (
              <p className="text-sm text-[var(--risk-critical)]" role="alert">
                {error}
              </p>
            )}
            {message && <p className="text-sm text-[var(--auth-forest)]">{message}</p>}
            <button className="btn btn-primary w-full" disabled={loading}>
              {loading ? "Gönderiliyor..." : "Doğrulama Kodu Gönder"}
            </button>
            <Link href="/login" className="btn btn-secondary w-full">
              Giriş Sayfasına Dön
            </Link>
          </form>
        ) : (
          <form className="space-y-4" onSubmit={onReset}>
            <AuthField
              id="reset_email"
              name="reset_email"
              label="E-posta"
              icon="mail"
              type="email"
              defaultValue={email.includes("@") ? email : ""}
              required
            />
            {demoCode && (
              <p className="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-900">
                MVP demo kodu: <strong>{demoCode}</strong>
              </p>
            )}
            <div>
              <p className="label">Doğrulama kodu</p>
              <OtpInputs value={code} onChange={setCode} />
            </div>
            <div>
              <AuthField
                id="new_password"
                name="new_password"
                label="Yeni şifre"
                icon="lock"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <PasswordRules password={password} />
            </div>
            {error && (
              <p className="text-sm text-[var(--risk-critical)]" role="alert">
                {error}
              </p>
            )}
            <button className="btn btn-primary w-full" disabled={loading}>
              {loading ? "Güncelleniyor..." : "Şifreyi Güncelle"}
            </button>
            <button
              type="button"
              className="btn btn-ghost w-full"
              onClick={() => setStep("request")}
            >
              ← Geri
            </button>
          </form>
        )}

        <div className="rounded-xl border border-[var(--auth-border)] bg-white px-4 py-3 text-sm text-[var(--auth-muted)]">
          Yardım için:{" "}
          <a className="font-medium text-[var(--auth-forest)]" href="mailto:destek@agritwin.ai">
            destek@agritwin.ai
          </a>
        </div>
      </div>
    </AuthSplitLayout>
  );
}
