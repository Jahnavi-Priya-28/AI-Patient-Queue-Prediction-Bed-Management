"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, Clock, Calendar, Ticket, LogOut } from "lucide-react";
import { apiClient } from "@/lib/api";
import { clearSession, requirePortalUser } from "@/lib/auth";
import { ThemeToggle } from "@/components/ThemeToggle";
import { AIAssistant } from "@/components/AIAssistant";

type QueueSummary = {
  status: string | null;
  queue_position: number | null;
  people_ahead: number;
  active_queue_length: number;
  estimated_wait_minutes: number | null;
  token_number: string | null;
  department_name: string | null;
  doctor_name: string | null;
  updated_at: string;
};

const emptySummary: QueueSummary = {
  status: null,
  queue_position: null,
  people_ahead: 0,
  active_queue_length: 0,
  estimated_wait_minutes: null,
  token_number: null,
  department_name: null,
  doctor_name: null,
  updated_at: "",
};

export default function PatientDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [queue, setQueue] = useState<QueueSummary>(emptySummary);
  const [queueLoading, setQueueLoading] = useState(true);
  const [queueError, setQueueError] = useState(false);

  const fetchQueue = useCallback(async () => {
    try {
      const response = await apiClient.get<QueueSummary>("/queue/my-summary");
      setQueue(response.data);
      setQueueError(false);
    } catch {
      setQueueError(true);
    } finally {
      setQueueLoading(false);
    }
  }, []);

  useEffect(() => {
    requirePortalUser("PATIENT")
      .then((verifiedUser) => {
        setUser(verifiedUser);
        return fetchQueue();
      })
      .catch((error: any) => { if (error.redirectTo) router.push(error.redirectTo); else { clearSession(); router.push("/login"); } });
  }, [fetchQueue, router]);

  useEffect(() => {
    if (!user) return;
    const interval = window.setInterval(fetchQueue, 10000);
    return () => window.clearInterval(interval);
  }, [fetchQueue, user]);

  const handleLogout = () => {
    clearSession();
    router.push("/login");
  };

  if (!user) return null;

  const queuePosition = queueLoading ? "Loading queue..." : queueError ? "Unable to load queue" : queue.queue_position ? `#${queue.queue_position} in Line` : "Not in queue";
  const estimatedWait = queueLoading ? "Loading..." : queueError ? "Unavailable" : queue.estimated_wait_minutes === null ? "-" : `~${queue.estimated_wait_minutes} min`;
  const token = queueLoading ? "-" : queueError ? "Unavailable" : queue.token_number || "-";
  const doctor = queueLoading ? "Loading..." : queueError ? "Unavailable" : queue.doctor_name || "Not assigned";
  const updated = queue.updated_at ? new Date(queue.updated_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "-";

  return (
    <div className="min-h-screen themed-canvas themed-ink flex flex-col">
      <header className="px-6 lg:px-16 h-20 themed-card flex items-center justify-between sticky top-0 z-50" style={{ borderBottomWidth: '1px', borderColor: 'var(--color-hairline)' }}>
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-full" style={{ backgroundColor: 'var(--color-ink)', color: 'var(--color-canvas-pure)' }}><Activity className="h-4 w-4" /></div>
          <span className="font-display font-light text-xl tracking-tight themed-ink">PatientFlow <span className="themed-ink-sec">Patient Portal</span></span>
        </div>
        <div className="flex items-center gap-3">
          <ThemeToggle />
          <span className="text-sm font-semibold themed-ink">{user.first_name} {user.last_name}</span>
          <button onClick={handleLogout} className="button-outline-on-light text-xs px-4 py-2"><LogOut className="w-4 h-4" /> Sign Out</button>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 lg:p-12 space-y-10">
        <AIAssistant role="PATIENT" />
        <div className="rounded-[16px] p-8 sm:p-10 shadow-stacked-tiny flex flex-col md:flex-row justify-between items-start md:items-center gap-6" style={{ backgroundColor: 'var(--color-aloe)', borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
          <div>
            <span className="inline-block text-[10px] font-mono uppercase tracking-widest px-3 py-1 rounded-pill mb-3" style={{ backgroundColor: 'var(--color-ink)', color: 'var(--color-canvas-pure)' }}>ACTIVE CHECK-IN STATUS</span>
            <h1 className="font-display text-4xl font-light tracking-tight themed-ink">Welcome back, {user.first_name}!</h1>
            <p className="themed-ink-sec text-sm mt-2">{queue.department_name ? `${queue.department_name} appointment queue` : "Your live appointment queue status"}</p>
          </div>
          <div className="themed-card px-8 py-5 rounded-[12px] text-center min-w-[200px] shadow-stacked-tiny" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
            <span className="block text-xs uppercase font-semibold themed-ink-sec tracking-eyebrow">YOUR TOKEN</span>
            <span className="font-display text-4xl font-light themed-ink tracking-wider mt-1 block">{token}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="themed-card p-8 rounded-[12px] shadow-stacked-tiny flex items-center gap-5" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
            <div className="p-3.5 rounded-full themed-badge" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}><Ticket className="w-6 h-6" /></div>
            <div><span className="text-xs themed-ink-sec font-semibold uppercase tracking-eyebrow">Queue Position</span><h3 className="font-display text-3xl font-light themed-ink mt-0.5">{queuePosition}</h3><p className="text-xs themed-ink-sec mt-1">{queueLoading ? "" : `${queue.people_ahead} people ahead`}</p></div>
          </div>
          <div className="themed-card p-8 rounded-[12px] shadow-stacked-tiny flex items-center gap-5" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
            <div className="p-3.5 rounded-full" style={{ backgroundColor: 'var(--color-aloe)', borderWidth: '1px', borderColor: 'var(--color-hairline)' }}><Clock className="w-6 h-6" /></div>
            <div><span className="text-xs themed-ink-sec font-semibold uppercase tracking-eyebrow">Estimated Wait</span><h3 className="font-display text-3xl font-light themed-ink mt-0.5">{estimatedWait}</h3><p className="text-xs themed-ink-sec mt-1">{queueLoading || queueError ? "" : `${queue.active_queue_length} patients currently waiting`}</p></div>
          </div>
          <div className="themed-card p-8 rounded-[12px] shadow-stacked-tiny flex items-center gap-5" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
            <div className="p-3.5 rounded-full" style={{ backgroundColor: 'var(--color-pistachio)', borderWidth: '1px', borderColor: 'var(--color-hairline)' }}><Calendar className="w-6 h-6" /></div>
            <div><span className="text-xs themed-ink-sec font-semibold uppercase tracking-eyebrow">Assigned Doctor</span><h3 className="font-display text-xl font-medium themed-ink mt-0.5">{doctor}</h3><p className="text-xs themed-ink-sec mt-1">Updated {updated}</p></div>
          </div>
        </div>
      </main>
    </div>
  );
}
