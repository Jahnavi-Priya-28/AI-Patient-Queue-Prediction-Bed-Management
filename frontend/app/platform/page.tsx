"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, Building2, LogOut } from "lucide-react";
import { apiClient } from "@/lib/api";
import { clearSession, requirePortalUser } from "@/lib/auth";
import { AIAssistant } from "@/components/AIAssistant";

export default function PlatformDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    requirePortalUser("SUPER_ADMIN")
      .then((verifiedUser) => {
        setUser(verifiedUser);
        return apiClient.get("/analytics/dashboard-metrics");
      })
      .then((response) => setMetrics(response.data))
      .catch((error: any) => {
        if (error.redirectTo) {
          router.push(error.redirectTo);
          return;
        }
        clearSession();
        router.push("/login");
      });
  }, [router]);

  if (!user || !metrics) {
    return <main className="min-h-screen themed-canvas themed-ink flex items-center justify-center text-sm themed-ink-sec">
        <AIAssistant role="SUPER_ADMIN" />Loading platform command center...</main>;
  }

  return (
    <main className="min-h-screen themed-canvas themed-ink">
      <header className="h-20 border-b border-hairline-light px-6 lg:px-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-black text-white rounded-full"><Activity className="h-4 w-4" /></div>
          <span className="font-display text-xl">PatientFlow Platform</span>
        </div>
        <button className="button-outline-on-light text-xs px-4 py-2" onClick={() => { clearSession(); router.push("/login"); }}>
          <LogOut className="w-4 h-4" /> Sign Out
        </button>
      </header>
      <section className="max-w-6xl mx-auto p-6 lg:p-12 space-y-8">
        <AIAssistant role="SUPER_ADMIN" />
        <div>
          <span className="inline-block bg-aloe-10 text-ink text-xs font-semibold px-3 py-1 rounded-pill mb-2">SUPER ADMIN</span>
          <h1 className="font-display text-4xl font-light">Platform Overview</h1>
          <p className="themed-ink-sec text-sm mt-2">Cross-organization operational visibility for {user.first_name} {user.last_name}.</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div className="themed-card border p-6 rounded-[8px]"><Building2 className="w-5 h-5 mb-4" /><div className="text-xs themed-ink-sec">Organizations</div><div className="font-display text-3xl mt-1">1</div></div>
          <div className="themed-card border p-6 rounded-[8px]"><div className="text-xs themed-ink-sec">Patients</div><div className="font-display text-3xl mt-1">{metrics.total_patients}</div></div>
          <div className="themed-card border p-6 rounded-[8px]"><div className="text-xs themed-ink-sec">Available Beds</div><div className="font-display text-3xl mt-1">{metrics.available_beds}</div></div>
        </div>
      </section>
    </main>
  );
}


