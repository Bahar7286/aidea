import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[var(--app-bg)]">
      <header className="border-b border-[var(--auth-border)] bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
          <span className="font-semibold text-[var(--auth-forest)]">AgriTwin AI</span>
          <nav className="flex gap-3 text-sm">
            <Link href="/login" className="text-[var(--auth-muted)] hover:text-[var(--auth-ink)]">
              Giriş
            </Link>
            <Link href="/register" className="btn btn-primary px-3 text-sm">
              Kayıt ol
            </Link>
          </nav>
        </div>
      </header>
      <div className="mx-auto max-w-5xl space-y-8 px-4 py-10">
        <section className="app-surface space-y-4 p-6 sm:p-8">
          <p className="text-sm font-semibold uppercase tracking-wide text-[var(--auth-forest)]">
            MVP Prototip
          </p>
          <h1 className="text-3xl font-bold leading-tight text-[var(--auth-ink)] sm:text-4xl">
            Toprak nemi ve sulama kararına odaklanan dijital ikiz
          </h1>
          <p className="max-w-2xl text-[var(--auth-muted)]">
            Manuel veri, IoT simülasyonu ve laboratuvar profilini birleştirerek sulama
            ihtiyacını açıklar — kullanıcı onayı olmadan otomasyon başlamaz.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link href="/register" className="btn btn-primary">
              Başla — Kayıt ol
            </Link>
            <Link href="/login" className="btn btn-secondary">
              Giriş yap
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}
