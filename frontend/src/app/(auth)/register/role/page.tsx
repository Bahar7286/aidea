"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AuthSplitLayout } from "@/components/auth/AuthSplitLayout";
import { AuthStepper } from "@/components/auth/AuthStepper";
import { api, getStoredUser, setSession } from "@/lib/api";

const ROLES = [
  {
    id: "farmer" as const,
    title: "Çiftçi",
    desc: "Kendi arazilerimin nem ve sulama kararlarını yönetmek istiyorum.",
  },
  {
    id: "agronomist" as const,
    title: "Ziraat Mühendisi",
    desc: "Çiftçilere danışmanlık vererek kararları birlikte izlemek istiyorum.",
  },
  {
    id: "cooperative" as const,
    title: "Kooperatif",
    desc: "Birden fazla üreticinin arazilerini ortak takip etmek istiyorum.",
  },
  {
    id: "consultant" as const,
    title: "Danışman",
    desc: "Müşteri tarlalarını uzaktan izleyip öneri üretmek istiyorum.",
  },
];

export default function RoleSelectPage() {
  const router = useRouter();
  const [role, setRole] = useState<(typeof ROLES)[number]["id"]>("farmer");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onContinue() {
    setLoading(true);
    setError("");
    try {
      const user = await api.updateRole(role);
      const token = localStorage.getItem("agritwin_token");
      if (token) setSession(token, user);
      router.push("/farms/new");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Rol kaydedilemedi.");
      if (!getStoredUser()) router.push("/login");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthSplitLayout
      panelTone="role"
      panelTitle="Size uygun deneyimi seçin."
      panelSubtitle="Rolünüze göre öneriler ve paneller şekillenir."
    >
      <AuthStepper current={3} />
      <div className="space-y-5">
        <div>
          <h1 className="text-2xl font-bold text-[var(--auth-ink)]">
            Sizin için en uygun kullanıcı türünü seçin.
          </h1>
        </div>

        <div className="space-y-2">
          {ROLES.map((item) => (
            <button
              key={item.id}
              type="button"
              className="role-card"
              data-selected={role === item.id}
              onClick={() => setRole(item.id)}
            >
              <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#e8f5e9] text-sm font-bold text-[var(--auth-forest)]">
                {item.title.slice(0, 1)}
              </span>
              <span className="flex-1">
                <span className="block font-semibold text-[var(--auth-ink)]">
                  {item.title}
                </span>
                <span className="mt-0.5 block text-xs text-[var(--auth-muted)]">
                  {item.desc}
                </span>
              </span>
              {role === item.id && (
                <span className="text-[var(--auth-forest)]" aria-hidden>
                  ✓
                </span>
              )}
            </button>
          ))}
        </div>

        {error && (
          <p className="text-sm text-[var(--risk-critical)]" role="alert">
            {error}
          </p>
        )}

        <div className="flex items-center justify-between gap-3">
          <Link href="/register/verify" className="btn btn-ghost">
            ← Geri
          </Link>
          <button
            type="button"
            className="btn btn-primary flex-1"
            disabled={loading}
            onClick={onContinue}
          >
            {loading ? "Kaydediliyor..." : "Devam Et →"}
          </button>
        </div>
      </div>
    </AuthSplitLayout>
  );
}
