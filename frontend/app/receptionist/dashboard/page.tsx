"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, UserPlus, Ticket, Bed, LogOut } from "lucide-react";
import { apiClient } from "@/lib/api";
import { clearSession, requirePortalUser } from "@/lib/auth";
import { ThemeToggle } from "@/components/ThemeToggle";
import { AIAssistant } from "@/components/AIAssistant";

export default function ReceptionistDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [beds, setBeds] = useState<any[]>([]);

  useEffect(() => {
    requirePortalUser("RECEPTIONIST")
      .then((verifiedUser) => { setUser(verifiedUser); fetchBeds(); })
      .catch((error: any) => { if (error.redirectTo) router.push(error.redirectTo); else { clearSession(); router.push("/login"); } });
  }, [router]);

  const fetchBeds = () => {
    apiClient.get("/beds").then((res) => {
      setBeds(res.data);
    }).catch(() => {});
  };

  const handleLogout = () => {
    localStorage.removeItem("patientflow_access_token");
    localStorage.removeItem("patientflow_user");
    router.push("/login");
  };

  if (!user) return null;

  return (
    <div className="min-h-screen themed-canvas themed-ink flex flex-col">
      <header className="px-6 lg:px-16 h-20 themed-card flex items-center justify-between sticky top-0 z-50" style={{ borderBottomWidth: '1px', borderColor: 'var(--color-hairline)' }}>
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-full" style={{ backgroundColor: 'var(--color-ink)', color: 'var(--color-canvas-pure)' }}>
            <Activity className="h-4 w-4" />
          </div>
          <span className="font-display font-light text-xl tracking-tight themed-ink">
            PatientFlow <span className="themed-ink-sec">Receptionist Desk</span>
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
        <AIAssistant role="RECEPTIONIST" />
        {/* Pistachio Feature Band */}
        <div className="rounded-[16px] p-8 sm:p-10 shadow-stacked-tiny grid grid-cols-1 md:grid-cols-2 gap-8" style={{ backgroundColor: 'var(--color-pistachio)', borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
          <div className="flex flex-col justify-between">
            <div>
              <span className="inline-block text-[10px] font-mono uppercase tracking-widest px-3 py-1 rounded-pill mb-3" style={{ backgroundColor: 'var(--color-ink)', color: 'var(--color-canvas-pure)' }}>
                RECEPTION SERVICES
              </span>
              <h2 className="font-display text-3xl font-light tracking-tight themed-ink">Patient Registration</h2>
              <p className="themed-ink-sec text-sm mt-2">Register new walk-in patients and issue digital profiles.</p>
            </div>
            <button onClick={() => router.push("/register")} className="button-primary-pill text-sm w-fit mt-6">
              <UserPlus className="w-4 h-4 mr-1" /> Register Patient Profile
            </button>
          </div>

          <div className="flex flex-col justify-between themed-card p-6 rounded-[12px] shadow-stacked-tiny" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
            <div>
              <span className="inline-block text-[10px] font-mono uppercase tracking-widest px-3 py-1 rounded-pill mb-3" style={{ backgroundColor: 'var(--color-aloe)', color: 'var(--color-ink)' }}>
                ATOMIC TRIAGE
              </span>
              <h2 className="font-display text-3xl font-light tracking-tight themed-ink">Patient Check-In</h2>
              <p className="themed-ink-sec text-sm mt-2">Issue concurrency-safe token (e.g. CARD-001) and run XGBoost model prediction.</p>
            </div>
            <button onClick={() => alert("Select appointment from patient list to check in")} className="button-aloe-pill text-sm w-fit mt-6">
              <Ticket className="w-4 h-4 mr-1" /> Issue Check-In Token
            </button>
          </div>
        </div>

        {/* Bed Grid */}
        <div className="themed-card p-8 rounded-[16px] shadow-stacked-tiny space-y-6" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
          <div className="flex justify-between items-center pb-4" style={{ borderBottomWidth: '1px', borderColor: 'var(--color-hairline)' }}>
            <div>
              <h3 className="font-display text-2xl font-light themed-ink">Ward Bed Occupancy Matrix</h3>
              <p className="themed-ink-sec text-xs mt-1">Real-time state machine tracking across hospital wards</p>
            </div>
            <span className="text-xs font-semibold px-4 py-1.5 rounded-pill" style={{ backgroundColor: 'var(--color-aloe)', color: 'var(--color-ink)', borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
              {beds.filter((b) => b.status === "AVAILABLE").length} Available Beds
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            {beds.map((bed) => (
              <div
                key={bed.id}
                className={`p-4 rounded-[12px] border text-center transition-all flex flex-col justify-between ${
                  bed.status === "AVAILABLE"
                    ? "border-emerald-400/30"
                    : bed.status === "OCCUPIED"
                    ? "bg-rose-500/10 border-rose-400/30 text-rose-400"
                    : bed.status === "CLEANING"
                    ? "bg-amber-500/10 border-amber-400/30 text-amber-400"
                    : "themed-badge"
                }`}
                style={bed.status === "AVAILABLE" ? { backgroundColor: 'var(--color-aloe)' } : bed.status !== "OCCUPIED" && bed.status !== "CLEANING" ? { borderColor: 'var(--color-hairline)' } : {}}
              >
                <div>
                  <Bed className="w-6 h-6 mx-auto mb-1 opacity-80" />
                  <span className="font-display text-lg font-light block">{bed.bed_number}</span>
                  <span className="text-[10px] font-mono font-bold uppercase tracking-wider block mt-1">
                    {bed.status}
                  </span>
                </div>

                {bed.status === "OCCUPIED" && (
                  <button
                    onClick={async () => {
                      await apiClient.post(`/beds/${bed.id}/release`);
                      fetchBeds();
                    }}
                    className="mt-3 text-xs font-semibold px-2 py-1 bg-rose-600 text-white rounded-pill hover:bg-rose-700 transition-colors"
                  >
                    Release Bed
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}




