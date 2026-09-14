"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, UserCheck, LogOut } from "lucide-react";
import { apiClient } from "@/lib/api";
import { clearSession, requirePortalUser } from "@/lib/auth";
import { ThemeToggle } from "@/components/ThemeToggle";

export default function DoctorDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [activeQueue, setActiveQueue] = useState<any[]>([]);
  const [calling, setCalling] = useState(false);

  useEffect(() => {
    requirePortalUser("DOCTOR")
      .then((verifiedUser) => { setUser(verifiedUser); fetchQueue(); })
      .catch((error: any) => { if (error.redirectTo) router.push(error.redirectTo); else { clearSession(); router.push("/login"); } });
  }, [router]);

  const fetchQueue = () => {
    apiClient.get("/queue").then((res) => {
      setActiveQueue(res.data);
    }).catch(() => {});
  };

  const handleCallNext = async () => {
    setCalling(true);
    try {
      await apiClient.post("/queue/call-next");
      fetchQueue();
    } catch (err: any) {
      alert(err.response?.data?.detail || "No waiting patients in queue.");
    } finally {
      setCalling(false);
    }
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
            PatientFlow <span className="themed-ink-sec">Doctor Console</span>
          </span>
        </div>

        <div className="flex items-center gap-3">
          <ThemeToggle />
          <span className="text-sm font-semibold themed-ink">
            Dr. {user.first_name} {user.last_name}
          </span>
          <button onClick={handleLogout} className="button-outline-on-light text-xs px-4 py-2">
            <LogOut className="w-4 h-4" /> Sign Out
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 lg:p-12 space-y-10">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 themed-card p-8 rounded-[16px] shadow-stacked-tiny" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
          <div>
            <span className="inline-block text-xs font-semibold px-3 py-1 rounded-pill mb-2" style={{ backgroundColor: 'var(--color-aloe)', color: 'var(--color-ink)' }}>
              TRIAGE & CONSULTATIONS
            </span>
            <h1 className="font-display text-3xl font-light themed-ink">Doctor Queue Console</h1>
            <p className="themed-ink-sec text-sm mt-1">Call next patient and compute ground-truth actual waiting duration.</p>
          </div>

          <button onClick={handleCallNext} disabled={calling} className="button-primary-pill text-base px-8 py-3.5">
            <UserCheck className="w-5 h-5 mr-1" /> Call Next Patient
          </button>
        </div>

        {/* Queue Table */}
        <div className="themed-card rounded-[16px] shadow-stacked-tiny overflow-hidden" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
          <div className="p-6 flex justify-between items-center themed-canvas" style={{ borderBottomWidth: '1px', borderColor: 'var(--color-hairline)' }}>
            <h3 className="font-display text-xl font-light themed-ink">Today&apos;s Patient Queue</h3>
            <span className="text-xs font-mono themed-ink-sec">{activeQueue.length} Patients Active</span>
          </div>

          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="themed-canvas themed-ink-sec text-xs font-semibold uppercase tracking-eyebrow" style={{ borderBottomWidth: '1px', borderColor: 'var(--color-hairline)' }}>
                <th className="py-4 px-6">Token</th>
                <th className="py-4 px-6">Priority</th>
                <th className="py-4 px-6">Status</th>
                <th className="py-4 px-6">Check-in Time</th>
                <th className="py-4 px-6">XGBoost Est.</th>
                <th className="py-4 px-6">Actions</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {activeQueue.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center themed-ink-sec font-normal">
                    No active patients in queue for today.
                  </td>
                </tr>
              ) : (
                activeQueue.map((item) => (
                  <tr key={item.id} className="transition-colors" style={{ borderBottomWidth: '1px', borderColor: 'var(--color-hairline)' }}>
                    <td className="py-4 px-6 font-display font-light text-lg themed-ink">{item.token_number}</td>
                    <td className="py-4 px-6">
                      <span className={`px-3 py-1 rounded-pill text-xs font-semibold ${
                        item.priority === 'EMERGENCY' ? 'bg-rose-100 text-rose-800 border border-rose-200' :
                        item.priority === 'URGENT' ? 'bg-amber-100 text-amber-800 border border-amber-200' : 'themed-badge'
                      }`} style={item.priority !== 'EMERGENCY' && item.priority !== 'URGENT' ? { borderWidth: '1px', borderColor: 'var(--color-hairline)' } : {}}>
                        {item.priority}
                      </span>
                    </td>
                    <td className="py-4 px-6 font-medium themed-ink">{item.status}</td>
                    <td className="py-4 px-6 themed-ink-sec">{new Date(item.check_in_time).toLocaleTimeString()}</td>
                    <td className="py-4 px-6 themed-ink font-semibold">{item.predicted_wait_minutes || 12} mins</td>
                    <td className="py-4 px-6">
                      <button
                        onClick={async () => {
                          await apiClient.post(`/queue/${item.id}/start-consultation`);
                          fetchQueue();
                        }}
                        className="button-aloe-pill text-xs px-3.5 py-1.5 mr-2"
                      >
                        Start
                      </button>
                      <button
                        onClick={async () => {
                          await apiClient.post(`/queue/${item.id}/complete-consultation`);
                          fetchQueue();
                        }}
                        className="button-primary-pill text-xs px-3.5 py-1.5"
                      >
                        Complete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}




