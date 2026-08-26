"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Activity, Lock, Mail, ArrowRight, AlertCircle } from "lucide-react";
import { apiClient } from "@/lib/api";
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

      if (user.role === "ADMIN") {
        router.push("/admin/dashboard");
      } else if (user.role === "DOCTOR") {
        router.push("/doctor/dashboard");
      } else if (user.role === "RECEPTIONIST") {
        router.push("/receptionist/dashboard");
      } else {
        router.push("/patient/dashboard");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Authentication failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8 themed-canvas themed-ink">
      {/* Floating Theme Toggle */}
      <div className="fixed top-6 right-6 z-50">
        <ThemeToggle />
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link href="/" className="inline-flex items-center gap-2.5 mb-6">
          <div className="p-2.5 rounded-full" style={{ backgroundColor: 'var(--color-ink)', color: 'var(--color-canvas-pure)' }}>
            <Activity className="h-5 w-5" />
          </div>
          <span className="font-display font-light text-2xl tracking-tight themed-ink">
            PatientFlow <span className="themed-ink-sec">AI</span>
          </span>
        </Link>
        <span className="inline-block text-xs font-semibold px-3 py-1 rounded-pill mb-3" style={{ backgroundColor: 'var(--color-aloe)', color: 'var(--color-ink)' }}>
          TRANSACTIONAL PORTAL
        </span>
        <h2 className="font-display text-3xl font-light tracking-tight themed-ink">
          Sign in to your account
        </h2>
        <p className="mt-2 text-sm themed-ink-sec">
          Access your role-based PatientFlow operational dashboard
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="themed-card py-10 px-6 shadow-stacked-tiny rounded-[16px] sm:px-10" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
          {error && (
            <div className="mb-5 p-4 bg-rose-50 border border-rose-200 text-rose-800 text-sm rounded-[12px] flex items-center gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-eyebrow mb-2 themed-ink-sec">
                Email Address
              </label>
              <div className="relative rounded-[8px]">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none themed-ink-tert">
                  <Mail className="h-4 w-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@patientflow.ai"
                  className="block w-full pl-10 pr-4 py-3 themed-input rounded-[8px] text-sm focus:outline-none focus:ring-2 focus:ring-current transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-eyebrow mb-2 themed-ink-sec">
                Password
              </label>
              <div className="relative rounded-[8px]">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none themed-ink-tert">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="block w-full pl-10 pr-4 py-3 themed-input rounded-[8px] text-sm focus:outline-none focus:ring-2 focus:ring-current transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="button-primary-pill w-full justify-center py-3.5 text-base"
            >
              {loading ? "Signing in..." : "Sign In"} <ArrowRight className="w-4 h-4 ml-1" />
            </button>
          </form>

          <div className="mt-8 pt-6 text-center text-xs themed-ink-sec" style={{ borderTopWidth: '1px', borderColor: 'var(--color-hairline)' }}>
            Don't have a patient account?{" "}
            <Link href="/register" className="font-semibold themed-ink underline underline-offset-4">
              Register Patient
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
