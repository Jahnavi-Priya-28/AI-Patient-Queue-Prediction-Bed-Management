"use client";

import { useMemo, useState } from "react";
import { Bot, Send, Sparkles } from "lucide-react";
import { apiClient } from "@/lib/api";
import type { UserRole } from "@/lib/auth";

type Props = { role: UserRole };

export function AIAssistant({ role }: Props) {
  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const suggestions = useMemo(() => {
    if (role === "PATIENT") return ["What's my appointment status?", "What's my estimated wait?"];
    if (role === "DOCTOR") return ["Summarize my workload", "Who is currently waiting?"];
    if (role === "RECEPTIONIST") return ["Where is the queue bottleneck?", "Show today's appointment situation"];
    return ["Summarize today's operations", "Which department needs attention?", "What should I focus on today?"];
  }, [role]);

  const ask = async (question = message) => {
    const trimmed = question.trim();
    if (!trimmed || loading) return;
    setLoading(true); setError(null); setAnswer(null); setMessage(trimmed);
    try {
      const response = await apiClient.post("/ai/chat", { message: trimmed });
      setAnswer(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "AI insights are temporarily unavailable. Standard PatientFlow features are still available.");
    } finally { setLoading(false); }
  };

  return (
    <section className="themed-card rounded-[16px] border p-6 shadow-stacked-tiny" style={{ borderColor: "var(--color-hairline)" }}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="p-2.5 rounded-full" style={{ backgroundColor: "var(--color-aloe)", color: "var(--color-ink)" }}><Bot className="w-5 h-5" /></div>
          <div><h2 className="font-display text-xl">PatientFlow AI Assistant</h2><p className="text-xs themed-ink-sec mt-1">Answers use only the information permitted for your role.</p></div>
        </div>
        <Sparkles className="w-4 h-4 themed-ink-tert" />
      </div>
      <div className="flex flex-wrap gap-2 mt-5">{suggestions.map((suggestion) => <button key={suggestion} type="button" onClick={() => ask(suggestion)} className="button-outline-on-light text-xs px-3 py-2">{suggestion}</button>)}</div>
      <form className="flex gap-2 mt-4" onSubmit={(event) => { event.preventDefault(); ask(); }}>
        <input value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Ask about your PatientFlow workspace" className="themed-input min-w-0 flex-1 rounded-[8px] px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-current" />
        <button type="submit" disabled={loading || !message.trim()} aria-label="Ask PatientFlow AI" className="button-primary-pill px-4"><Send className="w-4 h-4" /></button>
      </form>
      {loading && <p className="text-sm themed-ink-sec mt-4">Preparing an authorized answer...</p>}
      {error && <p className="text-sm text-rose-700 mt-4">{error}</p>}
      {answer && <div className="mt-5 border-t pt-4 themed-hairline"><p className="text-sm leading-6">{answer.summary}</p>{answer.key_findings?.length > 0 && <ul className="mt-3 space-y-1 text-sm themed-ink-sec">{answer.key_findings.map((item: string) => <li key={item}>• {item}</li>)}</ul>}{answer.recommendations?.length > 0 && <div className="mt-3 text-sm"><span className="font-semibold">Recommended:</span> {answer.recommendations.join(" ")}</div>}{!answer.available && <p className="mt-3 text-xs themed-ink-sec">Gemini is not configured or is temporarily unavailable.</p>}</div>}
    </section>
  );
}
