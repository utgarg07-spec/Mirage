import { useEffect, useMemo, useState } from "react";

const API_BASE = "http://localhost:8000";

function buildReportText(data) {
  if (!data || typeof data !== "object") return "No report data.";
  const lines = [];
  lines.push("MIRAGE FORENSIC BRIEF");
  lines.push("========================================");
  lines.push("");
  lines.push(`SESSION: ${data?.session?.session_id || "—"}`);
  lines.push(`IP: ${data?.session?.ip_address || "—"}`);
  lines.push(`USERNAME: ${data?.session?.username_tried || "—"}`);
  lines.push(`START: ${data?.session?.start_time || "—"}`);
  lines.push(`END: ${data?.session?.end_time || "—"}`);
  lines.push("");
  lines.push(`COMMAND COUNT: ${data?.command_count ?? "—"}`);
  lines.push("");
  lines.push("MITRE ATT&CK");
  lines.push("----------------------------------------");
  lines.push(`CURRENT STAGE: ${data?.mitre?.current_stage || "—"}`);
  lines.push(`NEXT STAGE: ${data?.mitre?.next_stage || "—"}`);
  lines.push(`CONFIDENCE: ${data?.mitre?.confidence ?? "—"}`);
  lines.push(`SKILL LEVEL: ${data?.mitre?.skill_level ?? "—"}`);
  lines.push("");
  lines.push("TECHNIQUES:");
  const tags = data?.technique_tags || data?.mitre?.technique_tags || [];
  if (tags.length === 0) lines.push("- none");
  else tags.forEach((t) => lines.push(`- ${t}`));
  lines.push("");
  lines.push("LAST COMMANDS:");
  const cmds = data?.last_commands || [];
  if (cmds.length === 0) lines.push("- none");
  else cmds.forEach((c) => lines.push(`- ${c}`));
  lines.push("");
  lines.push("HONEY FILES:");
  const hf = data?.honey_files || [];
  if (hf.length === 0) lines.push("- none");
  else hf.forEach((f) => lines.push(`- ${f}`));
  lines.push("");
  lines.push("BLOCKCHAIN:");
  lines.push(`AVAILABLE: ${data?.web3?.available ? "YES" : "NO"}`);
  if (data?.web3?.reason) lines.push(`REASON: ${data.web3.reason}`);
  lines.push("");
  lines.push("========================================");
  lines.push("END OF BRIEF");
  return lines.join("\n");
}

export default function ForensicModal({ sessionId, onClose }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);

  useEffect(() => {
    let alive = true;
    async function run() {
      setLoading(true);
      setError("");
      try {
        const res = await fetch(`${API_BASE}/forensics/${sessionId}`);
        if (!res.ok) throw new Error("forensics fetch failed");
        const json = await res.json();
        if (!alive) return;
        setData(json);
      } catch (e) {
        if (!alive) return;
        setError(e?.message || "failed");
      }
      if (!alive) return;
      setLoading(false);
    }
    if (sessionId) run();
    return () => {
      alive = false;
    };
  }, [sessionId]);

  const reportText = useMemo(() => buildReportText(data), [data]);

  function download() {
    const blob = new Blob([reportText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `mirage_forensics_${String(sessionId).slice(0, 8)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-6">
      <div className="w-full max-w-4xl rounded-2xl border border-green-900 bg-[#050607] shadow-[0_0_60px_rgba(34,211,238,0.08)] overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-green-900/60">
          <div className="flex items-center gap-3">
            <div className="text-xs tracking-widest text-green-300 font-semibold">ANALYSIS UNIT</div>
            <div className="text-[10px] px-2 py-0.5 rounded bg-red-600/20 border border-red-700 text-red-200 font-bold tracking-widest">
              CLASSIFIED
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-300 hover:text-white text-sm px-3 py-1 rounded border border-gray-800 bg-[#161b22]"
          >
            CLOSE
          </button>
        </div>

        <div className="p-5">
          {loading ? (
            <div className="flex items-center gap-3 text-green-300 font-mono">
              <div className="h-4 w-4 rounded-full border-2 border-green-400 border-t-transparent animate-spin" />
              <div className="tracking-widest text-sm">ANALYZING ATTACK PATTERNS...</div>
            </div>
          ) : error ? (
            <div className="text-red-300 font-mono text-sm">ERROR: {error}</div>
          ) : (
            <>
              <div className="rounded-xl border border-green-900/60 bg-black/40 p-4">
                <pre className="whitespace-pre-wrap font-mono text-sm text-green-200 leading-relaxed">
                  {reportText}
                </pre>
              </div>

              <div className="mt-4 flex items-center gap-3">
                <button
                  type="button"
                  onClick={download}
                  className="px-4 py-2 rounded-lg bg-cyan-500 text-black font-semibold hover:bg-cyan-400 transition"
                >
                  DOWNLOAD REPORT
                </button>
                <div className="text-xs text-gray-500 font-mono">session: {sessionId}</div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

