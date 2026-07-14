import Link from "next/link";
import { Leaf } from "lucide-react";
import { LandingFieldHero } from "@/components/landing/LandingFieldHero";

export default function HomePage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#081c15] text-white">
      {/* Full-bleed field atmosphere */}
      <div
        className="pointer-events-none absolute inset-0"
        aria-hidden
      >
        <div className="absolute inset-0 bg-gradient-to-br from-[#052016] via-[#1b4332] to-[#2d6a4f]" />
        <div className="absolute -left-24 top-10 h-[28rem] w-[28rem] rounded-full bg-lime-300/10 blur-3xl" />
        <div className="absolute -right-16 bottom-0 h-[22rem] w-[22rem] rounded-full bg-emerald-400/15 blur-3xl" />
        <div
          className="absolute inset-0 opacity-[0.12]"
          style={{
            backgroundImage:
              "radial-gradient(circle at 1px 1px, rgb(255 255 255 / 35%) 1px, transparent 0)",
            backgroundSize: "28px 28px",
          }}
        />
      </div>

      <header className="relative z-20">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-5 sm:px-8">
          <Link
            href="/"
            className="inline-flex items-center gap-2.5 text-lg font-semibold tracking-tight text-white"
          >
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/15 text-lime-300">
              <Leaf className="h-5 w-5" strokeWidth={2.25} aria-hidden />
            </span>
            AgriTwin AI
          </Link>
          <div className="flex items-center gap-2 sm:gap-3">
            <a
              href="/pitch/"
              className="rounded-xl px-3 py-2 text-sm font-semibold text-lime-300/95 underline-offset-4 transition hover:bg-white/10 hover:underline sm:px-4"
            >
              Sunum (9 sayfa)
            </a>
            <Link
              href="/login"
              className="rounded-xl border border-white/25 bg-white/10 px-4 py-2 text-sm font-semibold text-white backdrop-blur transition hover:bg-white/20"
            >
              Giriş
            </Link>
          </div>
        </div>
      </header>

      <main className="relative z-10">
        <section className="mx-auto grid min-h-[calc(100vh-5.5rem)] max-w-6xl items-center gap-10 px-5 pb-16 pt-6 sm:px-8 lg:grid-cols-[1.05fr_0.95fr] lg:gap-12 lg:pb-20 lg:pt-4">
          <div className="space-y-7">
            <p className="landing-fade-up text-sm font-semibold uppercase tracking-[0.18em] text-lime-300/90">
              AgriTwin AI
            </p>
            <h1 className="landing-fade-up landing-delay-1 max-w-xl text-4xl font-semibold leading-[1.12] tracking-tight text-white sm:text-5xl lg:text-[3.25rem]">
              Toprak nemini görün. Sulamayı güvenle kararlaştırın.
            </h1>
            <p className="landing-fade-up landing-delay-2 max-w-lg text-base leading-relaxed text-white/80 sm:text-lg">
              Simüle IoT, manuel ölçü ve laboratuvar profiliyle tek nem odak —
              sanal sulama yalnızca sizin onayınızla başlar.
            </p>
            <div className="landing-fade-up landing-delay-3 flex flex-wrap items-center gap-3">
              <Link
                href="/login"
                className="inline-flex min-h-11 items-center justify-center rounded-xl bg-lime-300 px-5 text-sm font-bold text-[#081c15] transition hover:bg-lime-200"
              >
                Giriş yap
              </Link>
              <Link
                href="/login#demo"
                className="inline-flex min-h-11 items-center justify-center rounded-xl border border-white/30 px-5 text-sm font-semibold text-white transition hover:bg-white/10"
              >
                Demo hesaplar
              </Link>
              <Link
                href="/register"
                className="text-sm font-medium text-white/65 underline-offset-4 hover:text-white hover:underline"
              >
                Yeni hesap
              </Link>
            </div>
            <p className="landing-fade-up landing-delay-4 text-xs text-white/50">
              MVP prototip · simülasyon verisi gerçek sensör iddiası taşımaz
            </p>
          </div>

          <div className="landing-fade-up landing-delay-2 relative min-h-[16rem] sm:min-h-[20rem] lg:min-h-[24rem]">
            <LandingFieldHero />
          </div>
        </section>
      </main>

      <footer className="relative z-20 border-t border-white/10">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-5 py-5 text-sm text-white/60 sm:px-8">
          <span>AgriTwin AI · MVP prototip</span>
          <a
            href="/pitch/"
            className="font-semibold text-lime-300/90 underline-offset-4 hover:text-lime-200 hover:underline"
          >
            Sunum (9 sayfa)
          </a>
        </div>
      </footer>
    </div>
  );
}
