"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AuthSplitLayout } from "@/components/auth/AuthSplitLayout";
import { AuthField } from "@/components/auth/AuthField";
import { api, setSession } from "@/lib/api";

const DEMO_PASSWORD = "Secret12";

const DEMO_ACCOUNTS = [
  { email: "admin@agritwin.demo", label: "Admin", hint: "Yönetim" },
  { email: "ciftci@agritwin.demo", label: "Çiftçi", hint: "Ana demo" },
  { email: "ziraat@agritwin.demo", label: "Ziraat", hint: "Danışman" },
  { email: "kooperatif@agritwin.demo", label: "Kooperatif", hint: "Koop" },
] as const;

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [remembered, setRemembered] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    const saved = localStorage.getItem("agritwin_remember") || "";
    setRemembered(saved);
    if (saved) setEmail(saved);
  }, []);

  function homeFor(role?: string) {
    return role === "admin" ? "/admin" : "/dashboard";
  }

  async function loginWith(creds: { email: string; password: string }, remember = false) {
    setError("");
    setLoading(true);
    try {
      const data = await api.login(creds);
      setSession(data.access_token, data.user);
      if (remember) {
        localStorage.setItem("agritwin_remember", creds.email);
      } else {
        localStorage.removeItem("agritwin_remember");
      }
      router.push(homeFor(data.user?.role));
      router.refresh();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Giriş başarısız.";
      setError(msg);
      if (msg.includes("doğrulanmamış")) {
        router.push(`/register/verify?email=${encodeURIComponent(creds.email)}`);
      }
    } finally {
      setLoading(false);
    }
  }

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    await loginWith(
      {
        email: String(form.get("email")),
        password: String(form.get("password")),
      },
      form.get("remember") === "on",
    );
  }

  async function demoLogin(demoEmail: string) {
    setEmail(demoEmail);
    setPassword(DEMO_PASSWORD);
    setError("");
    setLoading(true);
    try {
      const data = await api.demoLogin({
        email: demoEmail,
        password: DEMO_PASSWORD,
      });
      setSession(data.access_token, data.user);
      localStorage.removeItem("agritwin_remember");
      router.push(homeFor(data.user?.role));
      router.refresh();
    } catch (err) {
      try {
        await loginWith({ email: demoEmail, password: DEMO_PASSWORD }, false);
        return;
      } catch {
        setError(err instanceof Error ? err.message : "Demo giriş başarısız.");
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

        <form
          className="space-y-4"
          onSubmit={onSubmit}
          key={remembered || "empty"}
        >
          <AuthField
            id="email"
            name="email"
            label="E-posta veya Telefon"
            icon="user"
            placeholder="ornek@email.com veya 5XXXXXXXXX"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="username"
          />
          <AuthField
            id="password"
            name="password"
            label="Şifre"
            icon="lock"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
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

        <div id="demo" className="scroll-mt-8 space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-[var(--auth-muted)]">
            Demo hesaplar · {DEMO_PASSWORD}
          </p>
          <div className="grid grid-cols-2 gap-2">
            {DEMO_ACCOUNTS.map((acc) => (
              <button
                key={acc.email}
                type="button"
                disabled={loading}
                onClick={() => demoLogin(acc.email)}
                className="rounded-xl border border-[var(--auth-border)] bg-white px-3 py-2.5 text-left transition hover:border-[var(--auth-forest)] hover:bg-emerald-50/80 disabled:opacity-55"
              >
                <span className="block text-sm font-semibold text-[var(--auth-ink)]">
                  {acc.label}
                </span>
                <span className="mt-0.5 block truncate text-[10px] text-[var(--auth-muted)]">
                  {acc.hint} · {acc.email}
                </span>
              </button>
            ))}
          </div>
        </div>

        <div className="relative text-center text-xs text-[var(--auth-muted)]">
          <span className="relative z-10 bg-[var(--auth-bg)] px-2">veya</span>
          <div className="absolute left-0 right-0 top-1/2 border-t border-[var(--auth-border)]" />
        </div>

        <Link href="/register" className="btn btn-secondary w-full">
          Hesap Oluştur
        </Link>

        <p className="text-center text-xs text-[var(--auth-muted)]">
          <a
            href="/pitch/"
            className="font-semibold text-[var(--auth-accent)] underline-offset-4 hover:underline"
          >
            Sunum (9 sayfa)
          </a>
        </p>
      </div>
    </AuthSplitLayout>
  );
}
