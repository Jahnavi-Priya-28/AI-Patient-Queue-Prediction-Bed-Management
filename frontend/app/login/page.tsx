"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Activity, Lock, ArrowRight, AlertCircle, Mail } from "lucide-react";
import { apiClient } from "@/lib/api";
import { dashboardForRole, UserRole } from "@/lib/auth";
import { ThemeToggle } from "@/components/ThemeToggle";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await apiClient.post("/auth/login", { email, password });
      const { access_token, user } = res.data;
      localStorage.setItem("patientflow_access_token", access_token);
      localStorage.setItem("patientflow_user", JSON.stringify(user));
      router.push(dashboardForRole[user.role as UserRole] || "/patient/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8 themed-canvas themed-ink">
      <div className="fixed top-6 right-6 z-50"><ThemeToggle /></div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center px-4">
        <Link href="/" className="inline-flex items-center gap-2.5 mb-6">
          <div className="p-2.5 rounded-full" style={{ backgroundColor: "var(--color-ink)", color: "var(--color-canvas-pure)" }}>
            <Activity className="h-5 w-5" />
          </div>
          <span className="font-display font-light text-2xl tracking-tight themed-ink">PatientFlow <span className="themed-ink-sec">AI</span></span>
        </Link>
        <span className="inline-block text-xs font-semibold px-3 py-1 rounded-pill mb-3" style={{ backgroundColor: "var(--color-aloe)", color: "var(--color-ink)" }}>
          HOSPITAL OPERATIONS PLATFORM
        </span>
        <h2 className="font-display text-3xl font-light tracking-tight themed-ink">Sign in</h2>
        <p className="mt-2 text-sm themed-ink-sec">Use your work or patient email. Your role and hospital are verified by the backend.</p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4">
        <div className="themed-card py-10 px-6 shadow-stacked-tiny rounded-[16px] sm:px-10" style={{ borderWidth: "1px", borderColor: "var(--color-hairline)" }}>
          {error && <div className="mb-5 p-4 bg-rose-50 border border-rose-200 text-rose-800 text-sm rounded-[8px] flex items-center gap-2"><AlertCircle className="w-5 h-5 flex-shrink-0" /><span>{error}</span></div>}

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold uppercase mb-2 themed-ink-sec">Email</label>
              <div className="relative rounded-[8px]">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none themed-ink-tert"><Mail className="h-4 w-4" /></div>
                <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="admin@example.com" className="block w-full pl-10 pr-4 py-3 themed-input rounded-[8px] text-sm focus:outline-none focus:ring-2 focus:ring-current transition-all" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase mb-2 themed-ink-sec">Password</label>
              <div className="relative rounded-[8px]">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none themed-ink-tert"><Lock className="h-4 w-4" /></div>
                <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" className="block w-full pl-10 pr-4 py-3 themed-input rounded-[8px] text-sm focus:outline-none focus:ring-2 focus:ring-current transition-all" />
              </div>
            </div>

            <button type="submit" disabled={loading} className="button-primary-pill w-full justify-center py-3.5 text-base">
              {loading ? "Signing in..." : "Sign In"} <ArrowRight className="w-4 h-4 ml-1" />
            </button>
          </form>

          <div className="mt-7 flex items-center justify-between text-xs themed-ink-sec">
            <button type="button" className="font-semibold themed-ink underline underline-offset-4">Forgot password?</button>
            <Link href="/register" className="font-semibold themed-ink underline underline-offset-4">Create account</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
