import { apiClient } from "@/lib/api";

export type UserRole = "PATIENT" | "DOCTOR" | "RECEPTIONIST" | "HOSPITAL_ADMIN" | "SUPER_ADMIN";

export const dashboardForRole: Record<UserRole, string> = {
  PATIENT: "/patient/dashboard",
  DOCTOR: "/doctor/dashboard",
  RECEPTIONIST: "/receptionist/dashboard",
  HOSPITAL_ADMIN: "/admin/dashboard",
  SUPER_ADMIN: "/super-admin/dashboard",
};

export async function requirePortalUser(expectedRoles: UserRole | UserRole[]) {
  const token = typeof window !== "undefined" ? localStorage.getItem("patientflow_access_token") : null;
  if (!token) {
    throw new Error("UNAUTHENTICATED");
  }

  const response = await apiClient.get("/auth/me");
  const user = response.data;
  localStorage.setItem("patientflow_user", JSON.stringify(user));

  const allowed = Array.isArray(expectedRoles) ? expectedRoles : [expectedRoles];
  if (!allowed.includes(user.role as UserRole)) {
    const redirectTo = dashboardForRole[user.role as UserRole] || "/login";
    const error = new Error("WRONG_ROLE") as Error & { redirectTo?: string };
    error.redirectTo = redirectTo;
    throw error;
  }

  return user;
}

export function clearSession() {
  localStorage.removeItem("patientflow_access_token");
  localStorage.removeItem("patientflow_user");
}


