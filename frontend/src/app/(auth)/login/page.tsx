"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AuthSplitLayout } from "@/components/auth/AuthSplitLayout";
import { AuthField } from "@/components/auth/AuthField";
import { api, setSession } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [remembered, setRemembered] = useState("");

  useEffect(() => {
    setRemembered(localStorage.getItem("agritwin_remember") || "");
  }, []);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setLoading(true);
    const form = new FormData(e.currentTarget);
    const email = String(form.get("email"));
    try {
      const data = await api.login({
        email,
        password: String(form.get("password")),
      });
      setSession(data.access_token, data.user);
      if (form.get("remember") === "on") {
        localStorage.setItem("agritwin_remember", email);
      } else {
        localStorage.removeItem("agritwin_remember");
      }
      router.push("/dashboard");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Giriş başarısız.";
      setError(msg);
      if (msg.includes("doğrulanmamış")) {
        router.push(`/register/verify?email=${encodeURIComponent(email)}`);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthSplitLayout
      panelTone="login"
      panelTitle="Akıllı tarım, daha verimli yarınlar."
      panelSubtitle="Toprak nemi ve sulama kararlarını tek yerden yönetin."
    >
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--auth-ink)] sm:text-3xl">
            Hoş geldiniz!
          </h1>
          <p className="mt-1 text-sm text-[var(--auth-muted)]">
            Hesabınıza giriş yaparak tarlanızı yönetmeye devam edin.
          </p>
        </div>

        <form className="space-y-4" onSubmit={onSubmit} key={remembered || "empty"}>
          <AuthField
            id="email"
            name="email"
            label="E-posta veya Telefon"
            icon="user"
            placeholder="ornek@email.com veya 5XXXXXXXXX"
            defaultValue={remembered}
            required
            autoComplete="username"
          />
          <AuthField
            id="password"
            name="password"
            label="Şifre"
            icon="lock"
            type="password"
            required
            autoComplete="current-password"
          />

          <div className="flex items-center justify-between text-sm">
            <label className="flex items-center gap-2 text-[var(--auth-ink)]">
              <input
                type="checkbox"
                name="remember"
                defaultChecked={!!remembered}
                className="size-4 accent-[var(--auth-forest)]"
              />
              Beni Hatırla
            </label>
            <Link
              href="/forgot-password"
              className="font-medium text-[var(--auth-accent)] hover:underline"
            >
              Şifremi Unuttum
            </Link>
          </div>

          {error && (
            <p className="text-sm text-[var(--risk-critical)]" role="alert">
              {error}
            </p>
          )}

          <button className="btn btn-primary w-full" disabled={loading}>
            {loading ? "Giriş yapılıyor..." : "Giriş Yap →"}
          </button>
        </form>

        <div className="relative text-center text-xs text-[var(--auth-muted)]">
          <span className="relative z-10 bg-[var(--auth-bg)] px-2">veya</span>
          <div className="absolute left-0 right-0 top-1/2 border-t border-[var(--auth-border)]" />
        </div>

        <Link href="/register" className="btn btn-secondary w-full">
          Hesap Oluştur
        </Link>
      </div>
    </AuthSplitLayout>
  );
}
