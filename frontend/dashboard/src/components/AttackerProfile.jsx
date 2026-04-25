import { useMemo } from "react";

function skillMeta(level) {
  const n = Number(level || 1);
  if (n >= 3) return { label: "ADVANCED", cls: "bg-red-500/15 border-red-800 text-red-200 animate-pulse" };
  if (n === 2) return { label: "INTERMEDIATE", cls: "bg-yellow-500/15 border-yellow-800 text-yellow-200" };
  return { label: "SCRIPT KIDDIE", cls: "bg-gray-500/15 border-gray-800 text-gray-200" };
}

function formatDuration(start, end, active) {
  if (!start) return "—";
  const t0 = new Date(start).getTime();
  const t1 = end ? new Date(end).getTime() : Date.now();
  const dt = Math.max(0, t1 - t0);
  const m = Math.floor(dt / 60000);
  const s = Math.floor((dt % 60000) / 1000);
  return `${m}m ${String(s).padStart(2, "0")}s${active ? " (live)" : ""}`;
}

export default function AttackerProfile({ session, prediction }) {
  const meta = useMemo(() => skillMeta(prediction?.skill_level), [prediction?.skill_level]);
  const techniques = prediction?.technique_tags || [];

  if (!session) {
    return (
      <div className="rounded-xl bg-[#161b22] border border-gray-800 p-4">
        <div className="text-xs tracking-widest text-gray-300 font-semibold">ATTACKER PROFILE</div>
        <div className="mt-3 text-sm text-gray-500">No active session selected</div>
      </div>
    );
  }

  return (
    <div className="rounded-xl bg-[#161b22] border border-gray-800 p-4">
      <div className="text-xs tracking-widest text-gray-300 font-semibold">ATTACKER PROFILE</div>

      <div className="mt-3 flex items-center justify-between gap-3">
        <div className={["px-3 py-1 rounded-full border text-xs font-semibold tracking-wider", meta.cls].join(" ")}>
          {meta.label}
        </div>
        <div className="text-xs text-gray-400 font-mono">LVL {Number(prediction?.skill_level || 1)}</div>
      </div>

      <div className="mt-4 space-y-2 text-sm">
        <div className="flex items-center justify-between">
          <div className="text-gray-500">IP</div>
          <div className="text-gray-200 font-mono">{session.ip_address}</div>
        </div>
        <div className="flex items-center justify-between">
          <div className="text-gray-500">Session duration</div>
          <div className="text-gray-200 font-mono">
            {formatDuration(session.start_time, session.end_time, session.is_active)}
          </div>
        </div>
        <div className="flex items-center justify-between">
          <div className="text-gray-500">Commands executed</div>
          <div className="text-gray-200 font-mono">{Number(session.command_count || 0)}</div>
        </div>
      </div>

      <div className="mt-4">
        <div className="text-xs text-gray-400 tracking-widest">TECHNIQUES DETECTED</div>
        <div className="mt-2 flex flex-wrap gap-2">
          {techniques.length === 0 ? (
            <span className="text-xs text-gray-500">No techniques detected yet.</span>
          ) : (
            techniques.slice(0, 10).map((t) => (
              <span
                key={t}
                className="text-[10px] px-2 py-0.5 rounded-full bg-black/20 border border-gray-800 text-gray-200"
              >
                {t}
              </span>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

