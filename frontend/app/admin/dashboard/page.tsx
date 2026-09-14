"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, Users, Clock, Bed, Cpu, LogOut } from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { apiClient } from "@/lib/api";
import { clearSession, requirePortalUser } from "@/lib/auth";
import { AIAssistant } from "@/components/AIAssistant";

export default function AdminDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    requirePortalUser(["HOSPITAL_ADMIN", "SUPER_ADMIN"])
      .then((verifiedUser) => {
        setUser(verifiedUser);
        return apiClient.get("/analytics/dashboard-metrics");
      })
      .then((res) => setMetrics(res.data))
      .catch((err: any) => {
        if (err.redirectTo) {
          router.push(err.redirectTo);
          return;
        }
        clearSession();
        setError(err.response?.data?.detail || "Unable to load the administration command center.");
        router.push("/login");
      });
  }, [router]);

  const handleLogout = () => {
    clearSession();
    router.push("/login");
  };

  if (error) return <div className="min-h-screen themed-canvas themed-ink flex items-center justify-center p-6"><div className="themed-card rounded-[8px] border p-6 text-sm" style={{ borderColor: "var(--color-hairline)" }}>{error}</div></div>;
  if (!user || !metrics) return <div className="min-h-screen themed-canvas themed-ink flex items-center justify-center text-sm themed-ink-sec">Loading command center...</div>;

  return (
    <div className="min-h-screen bg-canvas-cream text-ink flex flex-col">
      <header className="px-6 lg:px-16 h-20 bg-canvas-light border-b border-hairline-light flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-black text-white rounded-full">
            <Activity className="h-4 w-4" />
          </div>
          <span className="font-display font-light text-xl tracking-tight text-ink">
            PatientFlow <span className="text-shade-50">Admin Analytics</span>
          </span>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm font-semibold text-ink">
            {user.first_name} {user.last_name} (Administrator)
          </span>
          <button
            onClick={handleLogout}
            className="button-outline-on-light text-xs px-4 py-2"
          >
            <LogOut className="w-4 h-4" /> Sign Out
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 lg:p-12 space-y-10">
        <AIAssistant role="HOSPITAL_ADMIN" />
        {/* Header Band */}
        <div>
          <span className="inline-block bg-aloe-10 text-ink text-xs font-semibold px-3 py-1 rounded-pill mb-2">
            OPERATIONAL COMMAND CENTER
          </span>
          <h1 className="font-display text-4xl font-light text-ink">Executive Hospital Metrics</h1>
          <p className="text-shade-50 text-sm mt-1">Live PostgreSQL aggregated operational metrics, queue depth, and bed utilization.</p>
        </div>

        {/* KPI Cards (card-pricing style on canvas-light) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-canvas-light p-8 rounded-[16px] border border-hairline-light shadow-stacked-tiny flex items-center gap-5">
            <div className="p-3.5 bg-canvas-cream text-black rounded-full border border-hairline-light">
              <Users className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs font-semibold text-shade-50 uppercase tracking-eyebrow">Total Patients</span>
              <h3 className="font-display text-3xl font-light text-ink mt-0.5">{metrics.total_patients}</h3>
            </div>
          </div>

          <div className="bg-canvas-light p-8 rounded-[16px] border border-hairline-light shadow-stacked-tiny flex items-center gap-5">
            <div className="p-3.5 bg-canvas-cream text-black rounded-full border border-hairline-light">
              <Clock className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs font-semibold text-shade-50 uppercase tracking-eyebrow">Waiting Queue</span>
              <h3 className="font-display text-3xl font-light text-ink mt-0.5">{metrics.waiting_patients}</h3>
            </div>
          </div>

          <div className="bg-canvas-light p-8 rounded-[16px] border border-hairline-light shadow-stacked-tiny flex items-center gap-5">
            <div className="p-3.5 bg-aloe-10 text-black rounded-full border border-emerald-300">
              <Bed className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs font-semibold text-shade-50 uppercase tracking-eyebrow">Available Beds</span>
              <h3 className="font-display text-3xl font-light text-ink mt-0.5">{metrics.available_beds}</h3>
            </div>
          </div>

          <div className="bg-canvas-light p-8 rounded-[16px] border border-hairline-light shadow-stacked-tiny flex items-center gap-5">
            <div className="p-3.5 bg-pistachio-10 text-black rounded-full border border-emerald-300">
              <Cpu className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs font-semibold text-shade-50 uppercase tracking-eyebrow">Avg Wait Time</span>
              <h3 className="font-display text-3xl font-light text-ink mt-0.5">{metrics.avg_wait_minutes} mins</h3>
            </div>
          </div>
        </div>

        {/* Recharts Visualizations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-canvas-light p-8 rounded-[16px] border border-hairline-light shadow-stacked-tiny space-y-6">
            <div>
              <h3 className="font-display text-xl font-light text-ink">Department Queue Density</h3>
              <p className="text-shade-50 text-xs mt-1">Patient queue distribution by clinical department</p>
            </div>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metrics.queue_by_department}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e4e4e7" />
                  <XAxis dataKey="department" stroke="#71717a" fontSize={11} tickLine={false} />
                  <YAxis stroke="#71717a" fontSize={11} tickLine={false} />
                  <Tooltip cursor={{ fill: '#fbfbf5' }} />
                  <Bar dataKey="waiting_count" fill="#000000" radius={[6, 6, 0, 0]} name="Waiting Patients" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-canvas-light p-8 rounded-[16px] border border-hairline-light shadow-stacked-tiny space-y-6">
            <div>
              <h3 className="font-display text-xl font-light text-ink">Ward Capacity vs Occupancy</h3>
              <p className="text-shade-50 text-xs mt-1">Bed availability comparison across hospital wards</p>
            </div>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metrics.bed_occupancy_by_ward}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e4e4e7" />
                  <XAxis dataKey="ward" stroke="#71717a" fontSize={11} tickLine={false} />
                  <YAxis stroke="#71717a" fontSize={11} tickLine={false} />
                  <Tooltip cursor={{ fill: '#fbfbf5' }} />
                  <Bar dataKey="total_beds" fill="#d4d4d8" radius={[6, 6, 0, 0]} name="Total Capacity" />
                  <Bar dataKey="occupied_beds" fill="#c1fbd4" radius={[6, 6, 0, 0]} name="Occupied" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}





