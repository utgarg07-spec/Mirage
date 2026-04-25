import { useMemo } from "react";

const STAGE_STYLES = {
  reconnaissance: "bg-blue-500/15 text-blue-300 border-blue-800",
  initial_access: "bg-yellow-500/15 text-yellow-300 border-yellow-800",
  execution: "bg-orange-500/15 text-orange-300 border-orange-800",
  privilege_escalation: "bg-red-500/15 text-red-300 border-red-800",
  collection: "bg-rose-500/15 text-rose-300 border-rose-800",
  exfiltration: "bg-purple-500/15 text-purple-300 border-purple-800",
  impact: "bg-red-500/20 text-red-200 border-red-700 animate-pulse",
  unknown: "bg-gray-500/15 text-gray-300 border-gray-800",
};

function stageStyle(stage) {
  return STAGE_STYLES[stage] || STAGE_STYLES.unknown;
}

function formatElapsed(startTime) {
  const t0 = new Date(startTime || Date.now()).getTime();
  const dt = Math.max(0, Date.now() - t0);
  const m = Math.floor(dt / 60000);
  const s = Math.floor((dt % 60000) / 1000);
  return `${m}m ${String(s).padStart(2, "0")}s`;
}

function skillStars(level) {
  const n = Math.max(1, Math.min(3, Number(level || 1)));
  return `${"★".repeat(n)}${"☆".repeat(3 - n)}`;
}

function maskIp(ip) {
  if (!ip) return "127.0.0.x";
  const parts = String(ip).split(".");
  if (parts.length === 4) return `${parts[0]}.${parts[1]}.${parts[2]}.x`;
  return ip;
}

export default function SessionList({ sessions, predictions, activeSessionId, setActiveSessionId }) {
  const sorted = useMemo(() => {
    const list = Array.isArray(sessions) ? [...sessions] : [];
    list.sort((a, b) => {
      const aActive = a.is_active ? 1 : 0;
      const bActive = b.is_active ? 1 : 0;
      if (aActive !== bActive) return bActive - aActive;
      return new Date(b.start_time).getTime() - new Date(a.start_time).getTime();
    });
    return list;
  }, [sessions]);

  const activeCount = useMemo(() => sorted.filter((s) => s.is_active).length, [sorted]);

  return (
    <div className="h-full flex flex-col">
      <div className="px-4 pt-4 pb-3 flex items-center justify-between">
        <div className="text-xs tracking-widest text-gray-300 font-semibold">ACTIVE SESSIONS</div>
        <div className="text-xs px-2 py-0.5 rounded-full bg-[#161b22] border border-gray-800 text-gray-300">
          {activeCount}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-4 space-y-3">
        {sorted.length === 0 ? (
          <div className="px-3 py-6 rounded-xl bg-[#161b22] border border-gray-800 text-gray-400 text-sm">
            No sessions yet. Waiting for attacker connection...
          </div>
        ) : (
          sorted.map((s) => {
            const pred = predictions?.[s.session_id] || {};
            const stage = pred.current_stage || "unknown";
            const selected = s.session_id === activeSessionId;
            return (
              <button
                key={s.session_id}
                type="button"
                onClick={() => setActiveSessionId(s.session_id)}
                className={[
                  "w-full text-left rounded-xl p-3 border transition",
                  selected ? "border-cyan-500 bg-cyan-950/10" : "border-gray-800 bg-[#161b22] hover:border-gray-700",
                ].join(" ")}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-sm text-gray-100 font-mono truncate">{maskIp(s.ip_address)}</div>
                    <div className="text-xs text-gray-500 font-mono">{formatElapsed(s.start_time)}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    {s.is_active ? <span className="h-2.5 w-2.5 rounded-full bg-green-400 animate-pulse" /> : null}
                  </div>
                </div>

                <div className="mt-3 flex items-center gap-2 flex-wrap">
                  <span className="text-[10px] px-2 py-0.5 rounded-full border border-gray-800 bg-black/25 text-gray-200 font-mono">
                    {s.username_tried || "unknown"}
                  </span>
                  <span className={["text-[10px] px-2 py-0.5 rounded-full border font-semibold", stageStyle(stage)].join(" ")}>
                    {String(stage).replaceAll("_", " ").toUpperCase()}
                  </span>
                </div>

                <div className="mt-3 text-xs font-mono text-gray-300">{skillStars(pred.skill_level)}</div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}

