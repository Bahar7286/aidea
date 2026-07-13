"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Building2,
  Check,
  GraduationCap,
  HandHelping,
  Sprout,
} from "lucide-react";
import { AuthSplitLayout } from "@/components/auth/AuthSplitLayout";
import { AuthStepper } from "@/components/auth/AuthStepper";
import { api, getStoredUser, setSession } from "@/lib/api";

const ROLES = [
  {
    id: "farmer" as const,
    title: "Çiftçi",
    desc: "Kendi arazilerimin nem ve sulama kararlarını yönetmek istiyorum.",
    icon: Sprout,
    tone: "bg-emerald-100 text-emerald-800",
  },
  {
    id: "agronomist" as const,
    title: "Ziraat Mühendisi",
    desc: "Çiftçilere danışmanlık vererek kararları birlikte izlemek istiyorum.",
    icon: GraduationCap,
    tone: "bg-sky-100 text-sky-800",
  },
  {
    id: "cooperative" as const,
    title: "Kooperatif",
    desc: "Birden fazla üreticinin arazilerini ortak takip etmek istiyorum.",
    icon: Building2,
    tone: "bg-amber-100 text-amber-900",
  },
  {
    id: "consultant" as const,
    title: "Danışman",
    desc: "Müşteri tarlalarını uzaktan izleyip öneri üretmek istiyorum.",
    icon: HandHelping,
    tone: "bg-lime-100 text-lime-900",
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
      wide
      panelTitle="Size uygun deneyimi seçin."
      panelSubtitle="Rolünüze göre öneriler ve paneller şekillenir."
    >
      <AuthStepper current={3} />
      <div className="space-y-5">
        <div>
          <h1 className="text-2xl font-bold text-[var(--auth-ink)] sm:text-3xl">
            Sizin için en uygun kullanıcı türünü seçin.
          </h1>
        </div>

        <div className="role-grid">
          {ROLES.map((item) => {
            const Icon = item.icon;
            const selected = role === item.id;
            return (
              <button
                key={item.id}
                type="button"
                className="role-card"
                data-selected={selected}
                onClick={() => setRole(item.id)}
              >
                <span
                  className={`mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${item.tone}`}
                >
                  <Icon className="h-5 w-5" strokeWidth={2.25} aria-hidden />
                </span>
                <span className="flex-1">
                  <span className="block font-semibold text-[var(--auth-ink)]">
                    {item.title}
                  </span>
                  <span className="mt-0.5 block text-xs text-[var(--auth-muted)]">
                    {item.desc}
                  </span>
                </span>
                {selected && (
                  <Check
                    className="h-5 w-5 shrink-0 text-[var(--auth-forest)]"
                    aria-hidden
                  />
                )}
              </button>
            );
          })}
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
