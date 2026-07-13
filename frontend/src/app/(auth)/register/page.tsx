"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AuthSplitLayout } from "@/components/auth/AuthSplitLayout";
import { AuthStepper } from "@/components/auth/AuthStepper";
import { AuthField, PasswordRules } from "@/components/auth/AuthField";
import { api } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [password, setPassword] = useState("");

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    const form = new FormData(e.currentTarget);
    if (form.get("terms") !== "on") {
      setError("Devam etmek için kullanım koşullarını kabul edin.");
      return;
    }
    setLoading(true);
    try {
      const email = String(form.get("email"));
      const result = await api.register({
        name: String(form.get("name")),
        phone: String(form.get("phone") || "") || undefined,
        email,
        password: String(form.get("password")),
      });
      if (result.demo_code) {
        sessionStorage.setItem("agritwin_demo_code", result.demo_code);
      }
      sessionStorage.setItem("agritwin_pending_email", result.email);
      router.push(`/register/verify?email=${encodeURIComponent(result.email)}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kayıt başarısız.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthSplitLayout
      panelTone="register"
      panelTitle="Tarlanızı dijital olarak yönetmeye başlayın."
      panelSubtitle="Hesap oluşturun, doğrulayın ve ilk arazinizi ekleyin."
    >
      <AuthStepper current={1} />
      <div className="space-y-5">
        <div>
          <h1 className="text-2xl font-bold text-[var(--auth-ink)]">Hesap oluşturun</h1>
          <p className="mt-1 text-sm text-[var(--auth-muted)]">
            Bilgilerinizi girin; bir sonraki adımda doğrulama kodu göndereceğiz.
          </p>
        </div>

        <form className="space-y-3" onSubmit={onSubmit}>
          <AuthField id="name" name="name" label="Ad Soyad" icon="user" required />
          <AuthField
            id="phone"
            name="phone"
            label="Telefon Numarası"
            icon="phone"
            placeholder="5XXXXXXXXX"
            inputMode="tel"
          />
          <AuthField
            id="email"
            name="email"
            label="E-posta Adresi"
            icon="mail"
            type="email"
            required
            autoComplete="email"
          />
          <div>
            <AuthField
              id="password"
              name="password"
              label="Şifre"
              icon="lock"
              type="password"
              required
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <PasswordRules password={password} />
          </div>

          <label className="flex items-start gap-2 text-sm text-[var(--auth-ink)]">
            <input
              type="checkbox"
              name="terms"
              className="mt-1 size-4 accent-[var(--auth-forest)]"
            />
            <span>
              <Link href="#" className="text-[var(--auth-accent)] underline">
                Kullanım koşulları
              </Link>{" "}
              ve{" "}
              <Link href="#" className="text-[var(--auth-accent)] underline">
                gizlilik politikasını
              </Link>{" "}
              kabul ediyorum.
            </span>
          </label>

          {error && (
            <p className="text-sm text-[var(--risk-critical)]" role="alert">
              {error}
            </p>
          )}

          <button className="btn btn-primary w-full" disabled={loading}>
            {loading ? "Kaydediliyor..." : "Devam Et →"}
          </button>
        </form>

        <p className="text-center text-sm text-[var(--auth-muted)]">
          Zaten hesabınız var mı?{" "}
          <Link href="/login" className="font-semibold text-[var(--auth-forest)]">
            Giriş yap
          </Link>
        </p>
      </div>
    </AuthSplitLayout>
  );
}
