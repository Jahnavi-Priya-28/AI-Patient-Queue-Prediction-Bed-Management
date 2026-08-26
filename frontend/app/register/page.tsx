"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Activity, Lock, Mail, Phone, ArrowRight, AlertCircle, CheckCircle } from "lucide-react";
import { apiClient } from "@/lib/api";
import { ThemeToggle } from "@/components/ThemeToggle";

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    phone: "",
    role: "PATIENT",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await apiClient.post("/auth/register", formData);
      setSuccess(true);
      setTimeout(() => {
        router.push("/login");
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8 themed-canvas themed-ink">
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
          PATIENT REGISTRATION
        </span>
        <h2 className="font-display text-3xl font-light tracking-tight themed-ink">
          Create Patient Profile
        </h2>
        <p className="mt-2 text-sm themed-ink-sec">
          Register to book appointments and track queue positions in real-time
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="themed-card py-10 px-6 shadow-stacked-tiny rounded-[16px] sm:px-10" style={{ borderWidth: '1px', borderColor: 'var(--color-hairline)' }}>
          {error && (
            <div className="mb-5 p-4 bg-rose-900/20 border border-rose-500/30 text-rose-300 text-sm rounded-[12px] flex items-center gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="mb-5 p-4 text-sm rounded-[12px] flex items-center gap-2" style={{ backgroundColor: 'var(--color-aloe)', color: 'var(--color-ink)' }}>
              <CheckCircle className="w-5 h-5 flex-shrink-0" />
              <span>Registration successful! Redirecting to login...</span>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-eyebrow mb-1.5 themed-ink-sec">
                  First Name
                </label>
                <input
                  type="text"
                  required
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  placeholder="John"
                  className="block w-full px-3.5 py-3 themed-input rounded-[8px] text-sm focus:outline-none focus:ring-2 focus:ring-current"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-eyebrow mb-1.5 themed-ink-sec">
                  Last Name
                </label>
                <input
                  type="text"
                  required
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  placeholder="Doe"
                  className="block w-full px-3.5 py-3 themed-input rounded-[8px] text-sm focus:outline-none focus:ring-2 focus:ring-current"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-eyebrow mb-1.5 themed-ink-sec">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none themed-ink-tert">
                  <Mail className="h-4 w-4" />
                </div>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="john.doe@example.com"
                  className="block w-full pl-10 pr-4 py-3 themed-input rounded-[8px] text-sm focus:outline-none focus:ring-2 focus:ring-current"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-eyebrow mb-1.5 themed-ink-sec">
                Phone Number
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none themed-ink-tert">
                  <Phone className="h-4 w-4" />
                </div>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="+1 (555) 000-0000"
                  className="block w-full pl-10 pr-4 py-3 themed-input rounded-[8px] text-sm focus:outline-none focus:ring-2 focus:ring-current"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-eyebrow mb-1.5 themed-ink-sec">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none themed-ink-tert">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder="At least 8 characters"
                  className="block w-full pl-10 pr-4 py-3 themed-input rounded-[8px] text-sm focus:outline-none focus:ring-2 focus:ring-current"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || success}
              className="button-primary-pill w-full justify-center py-3.5 text-base mt-2"
            >
              {loading ? "Creating account..." : "Register Patient Account"} <ArrowRight className="w-4 h-4 ml-1" />
            </button>
          </form>

          <div className="mt-8 pt-6 text-center text-xs themed-ink-sec" style={{ borderTopWidth: '1px', borderColor: 'var(--color-hairline)' }}>
            Already registered?{" "}
            <Link href="/login" className="font-semibold themed-ink underline underline-offset-4">
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
