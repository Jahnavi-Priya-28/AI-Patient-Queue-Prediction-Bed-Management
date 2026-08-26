import Link from "next/link";
import Image from "next/image";
import { Activity, ArrowRight, ShieldCheck, Clock, Cpu, Bed } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-canvas-night text-on-primary selection:bg-white selection:text-black">
      {/* Cinematic Top Navigation (nav-bar-dark) */}
      <header className="px-6 lg:px-16 h-20 flex items-center justify-between border-b border-white/10 bg-canvas-night/90 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-white text-black rounded-full">
            <Activity className="h-4 w-4" />
          </div>
          <span className="font-display font-light text-xl tracking-tight text-white">
            PatientFlow <span className="text-shade-40">AI</span>
          </span>
        </div>

        <nav className="flex items-center gap-4">
          <Link href="/login" className="button-outline-on-dark">
            Sign In
          </Link>
          <Link href="/register" className="button-primary-pill !bg-white !text-black hover:!bg-shade-30">
            Start Free Trial
          </Link>
        </nav>
      </header>

      {/* Cinematic Marketing Hero Band */}
      <main className="flex-1">
        <section className="pt-24 pb-16 px-6 lg:px-16 max-w-[1600px] mx-auto flex flex-col items-start">
          {/* All-Caps Eyebrow */}
          <span className="text-xs uppercase font-normal tracking-eyebrow text-shade-40 mb-6 block">
            PATIENTFLOW AI OPERATIONAL INTELLIGENCE PLATFORM
          </span>

          {/* Signature Display-XXL Headline: 96px, Weight 330, 2.4px Tracking */}
          <h1 className="font-display text-5xl sm:text-7xl lg:text-[96px] font-thin text-white tracking-display-xxl leading-none max-w-6xl">
            Predict waiting times. Optimize bed allocation.
          </h1>

          <p className="mt-8 text-lg sm:text-xl font-normal text-shade-40 max-w-2xl leading-relaxed">
            A production-grade healthcare intelligence system unifying XGBoost waiting time regression and LSTM multivariate department demand forecasting.
          </p>

          <div className="mt-10 flex flex-wrap gap-4 items-center">
            <Link href="/login" className="button-outline-on-dark text-base px-8 py-4">
              Access Operational Dashboard <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
            <a href="#features" className="text-sm font-medium text-shade-40 hover:text-white transition-colors px-4 py-2">
              Explore Operational Modules &rarr;
            </a>
          </div>
        </section>

        {/* Full-Bleed Merchant / Hospital Operational Photography */}
        <section className="w-full px-4 lg:px-12 my-12">
          <div className="relative w-full h-[480px] sm:h-[640px] rounded-[20px] overflow-hidden border border-white/10 shadow-dark-elevated">
            <Image
              src="/hero.jpg"
              alt="PatientFlow AI Command Center Operations"
              fill
              className="object-cover object-center"
              priority
            />
            <div className="absolute inset-0 bg-gradient-to-t from-canvas-night via-transparent to-transparent opacity-80" />
            <div className="absolute bottom-10 left-10 right-10 flex justify-between items-end">
              <div>
                <span className="text-xs font-mono uppercase text-link-mint tracking-wider">LIVE OPERATIONAL FEED</span>
                <p className="text-2xl font-display font-light text-white mt-1">Real-time triage and bed capacity management across 6 departments.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Cinematic Feature Grid (card-feature-cinematic on canvas-night-elevated) */}
        <section id="features" className="py-24 px-6 lg:px-16 border-t border-white/10 bg-canvas-night">
          <div className="max-w-[1600px] mx-auto space-y-16">
            <div className="max-w-3xl">
              <span className="text-xs uppercase tracking-eyebrow text-link-cool-1">ARCHITECTURE & CORE MACHINE LEARNING</span>
              <h2 className="font-display text-4xl sm:text-6xl font-thin text-white tracking-tight mt-3">
                Engineered for defensible operational precision.
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* Card 1 */}
              <div className="bg-canvas-night-elevated p-10 rounded-[12px] border border-hairline-dark shadow-dark-elevated flex flex-col justify-between space-y-6">
                <div>
                  <div className="p-3 bg-white/10 text-white rounded-full w-fit mb-6">
                    <Clock className="w-6 h-6" />
                  </div>
                  <h3 className="text-2xl font-medium text-white mb-3 font-display">
                    XGBoost Queue Regression
                  </h3>
                  <p className="text-shade-40 text-sm leading-relaxed">
                    Predicts waiting duration per queue entry based on live operational features: queue depth, active doctors, priority triage, and consultation velocity.
                  </p>
                </div>
                <div className="pt-4 border-t border-white/10 text-xs font-mono text-link-cool-1">
                  MAE: 6.17 Mins | R²: 0.995
                </div>
              </div>

              {/* Card 2 */}
              <div className="bg-canvas-night-elevated p-10 rounded-[12px] border border-hairline-dark shadow-dark-elevated flex flex-col justify-between space-y-6">
                <div>
                  <div className="p-3 bg-white/10 text-white rounded-full w-fit mb-6">
                    <Cpu className="w-6 h-6" />
                  </div>
                  <h3 className="text-2xl font-medium text-white mb-3 font-display">
                    LSTM Multi-Horizon Demand
                  </h3>
                  <p className="text-shade-40 text-sm leading-relaxed">
                    Multivariate sequential time-series forecasting arrival demand 1h, 6h, 12h, and 24h ahead across hospital departments.
                  </p>
                </div>
                <div className="pt-4 border-t border-white/10 text-xs font-mono text-link-cool-1">
                  1h, 6h, 12h, 24h Forecast Horizons
                </div>
              </div>

              {/* Card 3 */}
              <div className="bg-canvas-night-elevated p-10 rounded-[12px] border border-hairline-dark shadow-dark-elevated flex flex-col justify-between space-y-6">
                <div>
                  <div className="p-3 bg-white/10 text-white rounded-full w-fit mb-6">
                    <Bed className="w-6 h-6" />
                  </div>
                  <h3 className="text-2xl font-medium text-white mb-3 font-display">
                    Atomic Bed State Machine
                  </h3>
                  <p className="text-shade-40 text-sm leading-relaxed">
                    Concurrency-safe state transitions (Available, Occupied, Cleaning, Maintenance) preventing over-assignment across hospital wards.
                  </p>
                </div>
                <div className="pt-4 border-t border-white/10 text-xs font-mono text-link-cool-1">
                  ACID Concurrency Controls
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Cinematic Footer (footer-dark) */}
      <footer className="bg-canvas-night border-t border-white/10 py-16 px-6 lg:px-16 text-shade-40 text-sm">
        <div className="max-w-[1600px] mx-auto grid grid-cols-1 md:grid-cols-4 gap-10 mb-12">
          <div>
            <span className="font-display font-light text-lg text-white block mb-4">PatientFlow AI</span>
            <p className="text-xs text-link-cool-2 leading-relaxed">
              Production-Grade AI Patient Queue Prediction & Bed Management System. Modular Monolith Architecture.
            </p>
          </div>
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-eyebrow text-white mb-4">System Modules</h4>
            <ul className="space-y-2 text-xs">
              <li><Link href="/login" className="hover:text-white transition-colors text-link-cool-1">Patient Portal</Link></li>
              <li><Link href="/login" className="hover:text-white transition-colors text-link-cool-1">Doctor Portal</Link></li>
              <li><Link href="/login" className="hover:text-white transition-colors text-link-cool-1">Receptionist Desk</Link></li>
              <li><Link href="/login" className="hover:text-white transition-colors text-link-cool-1">Admin Dashboard</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-eyebrow text-white mb-4">Machine Learning</h4>
            <ul className="space-y-2 text-xs">
              <li className="text-link-cool-2">XGBoost Wait Time Regression</li>
              <li className="text-link-cool-2">LSTM Multi-Horizon Forecaster</li>
              <li className="text-link-cool-2">Synthetic Governance Dataset</li>
            </ul>
          </div>
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-eyebrow text-white mb-4">Design Language</h4>
            <p className="text-xs text-link-cool-2">
              Dual-Track Layout System ({`{colors.canvas-night}`} & {`{colors.canvas-cream}`}) with OpenType ss03 typography.
            </p>
          </div>
        </div>
        <div className="max-w-[1600px] mx-auto pt-8 border-t border-white/10 flex flex-col sm:flex-row justify-between text-xs text-link-cool-2">
          <span>&copy; 2026 PatientFlow AI. All rights reserved.</span>
          <span>Project ID: 102 | Modular Monolith (PostgreSQL + FastAPI + Next.js)</span>
        </div>
      </footer>
    </div>
  );
}
