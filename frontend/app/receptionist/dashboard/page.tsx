"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, UserPlus, Ticket, Bed, LogOut, RefreshCw } from "lucide-react";
import { apiClient } from "@/lib/api";
import { clearSession, requirePortalUser } from "@/lib/auth";
import { ThemeToggle } from "@/components/ThemeToggle";
import { AIAssistant } from "@/components/AIAssistant";

type Appointment = { id: number; appointment_time: string; status: string; priority: string; patient?: { first_name?: string; last_name?: string; email?: string }; doctor?: { first_name?: string; last_name?: string }; department?: { name?: string } };
type QueueEntry = { appointment_id: number; token_number: string; status: string; patient?: { first_name?: string; last_name?: string }; department?: { name?: string } };

const today = () => new Date().toISOString().slice(0, 10);

export default function ReceptionistDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [beds, setBeds] = useState<any[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [queue, setQueue] = useState<QueueEntry[]>([]);
  const [queueLoading, setQueueLoading] = useState(true);
  const [queueError, setQueueError] = useState<string | null>(null);
  const [checkInError, setCheckInError] = useState<string | null>(null);
  const [checkingIn, setCheckingIn] = useState<number | null>(null);

  const fetchQueueData = useCallback(async () => {
    setQueueLoading(true);
    try {
      const [appointmentResponse, queueResponse, bedResponse] = await Promise.all([
        apiClient.get<Appointment[]>("/appointments", { params: { appt_date: today() } }),
        apiClient.get<QueueEntry[]>("/queue"),
        apiClient.get<any[]>("/beds"),
      ]);
      setAppointments(appointmentResponse.data);
      setQueue(queueResponse.data);
      setBeds(bedResponse.data);
      setQueueError(null);
    } catch (error: any) {
      setQueueError(error.response?.data?.detail || "Unable to load queue");
    } finally {
      setQueueLoading(false);
    }
  }, []);

  useEffect(() => {
    requirePortalUser("RECEPTIONIST")
      .then((verifiedUser) => { setUser(verifiedUser); return fetchQueueData(); })
      .catch((error: any) => { if (error.redirectTo) router.push(error.redirectTo); else { clearSession(); router.push("/login"); } });
  }, [fetchQueueData, router]);

  useEffect(() => {
    if (!user) return;
    const interval = window.setInterval(fetchQueueData, 10000);
    return () => window.clearInterval(interval);
  }, [fetchQueueData, user]);

  const checkedInAppointmentIds = useMemo(() => new Set(queue.map((entry) => entry.appointment_id)), [queue]);
  const checkInAppointments = appointments.filter((appointment) => !checkedInAppointmentIds.has(appointment.id) && ["SCHEDULED", "CONFIRMED"].includes(appointment.status));
  const activeQueue = queue.filter((entry) => ["WAITING", "CALLED", "IN_CONSULTATION"].includes(entry.status));

  const checkIn = async (appointmentId: number) => {
    setCheckingIn(appointmentId);
    setCheckInError(null);
    try {
      await apiClient.post("/queue/check-in", { appointment_id: appointmentId });
      await fetchQueueData();
    } catch (error: any) {
      setCheckInError(error.response?.data?.detail || "Unable to check in this appointment");
    } finally {
      setCheckingIn(null);
    }
  };

  const handleLogout = () => { clearSession(); router.push("/login"); };

  if (!user) return null;

  return (
    <div className="min-h-screen themed-canvas themed-ink flex flex-col">
      <header className="px-6 lg:px-16 h-20 themed-card flex items-center justify-between sticky top-0 z-50" style={{ borderBottomWidth: '1px', borderColor: 'var(--color-hairline)' }}>
        <div className="flex items-center gap-3"><div className="p-2.5 rounded-full" style={{ backgroundColor: 'var(--color-ink)', color: 'var(--color-canvas-pure)' }}><Activity className="h-4 w-4" /></div><span className="font-display font-light text-xl tracking-tight themed-ink">PatientFlow <span className="themed-ink-sec">Receptionist Desk</span></span></div>
        <div className="flex items-center gap-3"><ThemeToggle /><span className="text-sm font-semibold themed-ink">{user.first_name} {user.last_name}</span><button onClick={handleLogout} className="button-outline-on-light text-xs px-4 py-2"><LogOut className="w-4 h-4" /> Sign Out</button></div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 lg:p-12 space-y-10">
        <AIAssistant role="RECEPTIONIST" />
        <div className="rounded-[16px] p-8 sm:p-10 shadow-stacked-tiny grid grid-cols-1 md:grid-cols-2 gap-8" style={{ backgroundColor: 'var(--color-pistachio)', borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
          <div className="flex flex-col justify-between"><div><span className="inline-block text-[10px] font-mono uppercase tracking-widest px-3 py-1 rounded-pill mb-3" style={{ backgroundColor: 'var(--color-ink)', color: 'var(--color-canvas-pure)' }}>RECEPTION SERVICES</span><h2 className="font-display text-3xl font-light tracking-tight themed-ink">Patient Registration</h2><p className="themed-ink-sec text-sm mt-2">Register new walk-in patients and issue digital profiles.</p></div><button onClick={() => router.push("/register")} className="button-primary-pill text-sm w-fit mt-6"><UserPlus className="w-4 h-4 mr-1" /> Register Patient Profile</button></div>
          <div className="themed-card p-6 rounded-[12px] shadow-stacked-tiny" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
            <div className="flex items-center justify-between"><div><span className="inline-block text-[10px] font-mono uppercase tracking-widest px-3 py-1 rounded-pill mb-3" style={{ backgroundColor: 'var(--color-aloe)', color: 'var(--color-ink)' }}>ATOMIC TRIAGE</span><h2 className="font-display text-3xl font-light tracking-tight themed-ink">Patient Check-In</h2></div><button type="button" onClick={fetchQueueData} aria-label="Refresh queue" className="button-outline-on-light p-2"><RefreshCw className="w-4 h-4" /></button></div>
            <p className="themed-ink-sec text-sm mt-2">Select today&apos;s appointment to issue a real queue token and calculate its wait prediction.</p>
            {checkInError && <p className="text-sm text-rose-700 mt-4">{checkInError}</p>}
            <div className="mt-5 space-y-2 max-h-64 overflow-auto">
              {queueLoading && <p className="text-sm themed-ink-sec">Loading appointments...</p>}
              {!queueLoading && checkInAppointments.length === 0 && <p className="text-sm themed-ink-sec">No appointments are ready for check-in.</p>}
              {checkInAppointments.map((appointment) => <div key={appointment.id} className="flex items-center justify-between gap-3 border-t pt-3 themed-hairline"><div className="min-w-0"><p className="text-sm font-semibold truncate">{appointment.patient?.first_name} {appointment.patient?.last_name}</p><p className="text-xs themed-ink-sec">{appointment.department?.name || "Department"} · {appointment.appointment_time}</p></div><button type="button" onClick={() => checkIn(appointment.id)} disabled={checkingIn === appointment.id} className="button-aloe-pill text-xs px-3 py-2 whitespace-nowrap"><Ticket className="w-4 h-4" />{checkingIn === appointment.id ? "Checking in..." : "Check in"}</button></div>)}
            </div>
          </div>
        </div>

        <div className="themed-card p-8 rounded-[16px] shadow-stacked-tiny space-y-6" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
          <div className="flex justify-between items-center pb-4" style={{ borderBottomWidth: '1px', borderColor: 'var(--color-hairline)' }}><div><h3 className="font-display text-2xl font-light themed-ink">Live Waiting Queue</h3><p className="themed-ink-sec text-xs mt-1">{queueLoading ? "Loading queue..." : queueError || `${activeQueue.length} active patients`} </p></div><span className="text-xs font-semibold px-4 py-1.5 rounded-pill" style={{ backgroundColor: 'var(--color-aloe)', color: 'var(--color-ink)', borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>Updated every 10 seconds</span></div>
          {queueError && <p className="text-sm text-rose-700">{queueError}</p>}
          {!queueLoading && !queueError && activeQueue.length === 0 && <p className="text-sm themed-ink-sec">No active patients in the waiting queue.</p>}
          <div className="space-y-2">{activeQueue.map((entry, index) => <div key={entry.appointment_id} className="flex items-center justify-between border-t pt-3 themed-hairline"><div><span className="font-mono text-sm font-semibold">{entry.token_number}</span><span className="ml-3 text-sm">{entry.patient?.first_name} {entry.patient?.last_name}</span></div><span className="text-xs themed-ink-sec">{entry.status}</span></div>)}</div>
        </div>

        <div className="themed-card p-8 rounded-[16px] shadow-stacked-tiny space-y-6" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}><div className="flex justify-between items-center pb-4" style={{ borderBottomWidth: '1px', borderColor: 'var(--color-hairline)' }}><div><h3 className="font-display text-2xl font-light themed-ink">Ward Bed Occupancy Matrix</h3><p className="themed-ink-sec text-xs mt-1">Real-time state machine tracking across hospital wards</p></div><span className="text-xs font-semibold px-4 py-1.5 rounded-pill" style={{ backgroundColor: 'var(--color-aloe)', color: 'var(--color-ink)', borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>{beds.filter((b) => b.status === "AVAILABLE").length} Available Beds</span></div><div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">{beds.map((bed) => <div key={bed.id} className={`p-4 rounded-[12px] border text-center transition-all flex flex-col justify-between ${bed.status === "AVAILABLE" ? "border-emerald-400/30" : bed.status === "OCCUPIED" ? "bg-rose-500/10 border-rose-400/30 text-rose-400" : bed.status === "CLEANING" ? "bg-amber-500/10 border-amber-400/30 text-amber-400" : "themed-badge"}`} style={bed.status === "AVAILABLE" ? { backgroundColor: 'var(--color-aloe)' } : bed.status !== "OCCUPIED" && bed.status !== "CLEANING" ? { borderColor: 'var(--color-hairline)' } : {}}><div><Bed className="w-6 h-6 mx-auto mb-1 opacity-80" /><span className="font-display text-lg font-light block">{bed.bed_number}</span><span className="text-[10px] font-mono font-bold uppercase tracking-wider block mt-1">{bed.status}</span></div>{bed.status === "OCCUPIED" && <button onClick={async () => { await apiClient.post(`/beds/${bed.id}/release`); fetchQueueData(); }} className="mt-3 text-xs font-semibold px-2 py-1 bg-rose-600 text-white rounded-pill hover:bg-rose-700 transition-colors">Release Bed</button>}</div>)}</div></div>
      </main>
    </div>
  );
}
