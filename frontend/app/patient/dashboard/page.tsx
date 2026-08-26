"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Activity, Clock, Calendar, Ticket, LogOut } from "lucide-react";
import { apiClient } from "@/lib/api";
import { ThemeToggle } from "@/components/ThemeToggle";

export default function PatientDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const storedUser = localStorage.getItem("patientflow_user");
    if (!storedUser) {
      router.push("/login");
      return;
    }
    setUser(JSON.parse(storedUser));
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("patientflow_access_token");
    localStorage.removeItem("patientflow_user");
    router.push("/login");
  };

  if (!user) return null;

  return (
    <div className="min-h-screen themed-canvas themed-ink flex flex-col">
      {/* Transactional Nav */}
      <header className="px-6 lg:px-16 h-20 themed-card flex items-center justify-between sticky top-0 z-50" style={{ borderBottomWidth: '1px', borderColor: 'var(--color-hairline)' }}>
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-full" style={{ backgroundColor: 'var(--color-ink)', color: 'var(--color-canvas-pure)' }}>
            <Activity className="h-4 w-4" />
          </div>
          <span className="font-display font-light text-xl tracking-tight themed-ink">
            PatientFlow <span className="themed-ink-sec">Patient Portal</span>
          </span>
        </div>

        <div className="flex items-center gap-3">
          <ThemeToggle />
          <span className="text-sm font-semibold themed-ink">
            {user.first_name} {user.last_name}
          </span>
          <button onClick={handleLogout} className="button-outline-on-light text-xs px-4 py-2">
            <LogOut className="w-4 h-4" /> Sign Out
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 lg:p-12 space-y-10">
        {/* Featured Banner */}
        <div className="rounded-[16px] p-8 sm:p-10 shadow-stacked-tiny flex flex-col md:flex-row justify-between items-start md:items-center gap-6" style={{ backgroundColor: 'var(--color-aloe)', borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
          <div>
            <span className="inline-block text-[10px] font-mono uppercase tracking-widest px-3 py-1 rounded-pill mb-3" style={{ backgroundColor: 'var(--color-ink)', color: 'var(--color-canvas-pure)' }}>
              ACTIVE CHECK-IN STATUS
            </span>
            <h1 className="font-display text-4xl font-light tracking-tight themed-ink">
              Welcome back, {user.first_name}!
            </h1>
            <p className="themed-ink-sec text-sm mt-2">
              You are checked in for General Medicine Consultation at Hospital Central.
            </p>
          </div>
          <div className="themed-card px-8 py-5 rounded-[12px] text-center min-w-[200px] shadow-stacked-tiny" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
            <span className="block text-xs uppercase font-semibold themed-ink-sec tracking-eyebrow">YOUR TOKEN</span>
            <span className="font-display text-4xl font-light themed-ink tracking-wider mt-1 block">GEN-004</span>
          </div>
        </div>

        {/* Queue Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="themed-card p-8 rounded-[12px] shadow-stacked-tiny flex items-center gap-5" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
            <div className="p-3.5 rounded-full themed-badge" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
              <Ticket className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs themed-ink-sec font-semibold uppercase tracking-eyebrow">Queue Position</span>
              <h3 className="font-display text-3xl font-light themed-ink mt-0.5">#2 in Line</h3>
            </div>
          </div>

          <div className="themed-card p-8 rounded-[12px] shadow-stacked-tiny flex items-center gap-5" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
            <div className="p-3.5 rounded-full" style={{ backgroundColor: 'var(--color-aloe)', borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
              <Clock className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs themed-ink-sec font-semibold uppercase tracking-eyebrow">XGBoost Estimated Wait</span>
              <h3 className="font-display text-3xl font-light themed-ink mt-0.5">~14.5 Mins</h3>
            </div>
          </div>

          <div className="themed-card p-8 rounded-[12px] shadow-stacked-tiny flex items-center gap-5" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
            <div className="p-3.5 rounded-full" style={{ backgroundColor: 'var(--color-pistachio)', borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
              <Calendar className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs themed-ink-sec font-semibold uppercase tracking-eyebrow">Assigned Doctor</span>
              <h3 className="font-display text-xl font-medium themed-ink mt-0.5">Dr. Michael Taylor</h3>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
