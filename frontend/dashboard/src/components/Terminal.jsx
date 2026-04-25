import { useEffect, useMemo, useRef, useState } from "react";

const STAGE_COLOR = {
  reconnaissance: "text-blue-300",
  initial_access: "text-yellow-300",
  execution: "text-orange-300",
  privilege_escalation: "text-red-300",
  collection: "text-rose-300",
  exfiltration: "text-purple-300",
  impact: "text-red-200",
  unknown: "text-gray-300",
};

function stageColor(stage) {
  return STAGE_COLOR[stage] || STAGE_COLOR.unknown;
}

function shortId(id) {
  if (!id) return "—";
  const s = String(id);
  return s.length <= 10 ? s : `${s.slice(0, 6)}…${s.slice(-4)}`;
}

function fmtTs(iso) {
  try {
    const d = new Date(iso);
    return `${String(d.getUTCHours()).padStart(2, "0")}:${String(d.getUTCMinutes()).padStart(2, "0")}:${String(
      d.getUTCSeconds(),
    ).padStart(2, "0")}`;
  } catch {
    return "??:??:??";
  }
}

export default function Terminal({ commands = [], prediction = {}, sessionId }) {
  const bottomRef = useRef(null);
  const [flashIdx, setFlashIdx] = useState(-1);
  const [honeyPing, setHoneyPing] = useState(false);

  const stage = prediction?.current_stage || "unknown";

  const confidencePct = useMemo(() => {
    const c = Number(prediction?.confidence || 0);
    return `${Math.max(0, Math.min(100, Math.round(c * 100)))}%`;
  }, [prediction]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    if (commands.length > 0) {
      const t0 = setTimeout(() => setFlashIdx(commands.length - 1), 0);
      const t1 = setTimeout(() => setFlashIdx(-1), 450);
      return () => {
        clearTimeout(t0);
        clearTimeout(t1);
      };
    }
    return undefined;
  }, [commands.length]);

  useEffect(() => {
    if (Array.isArray(prediction?.honey_files) && prediction.honey_files.length > 0) {
      const t0 = setTimeout(() => setHoneyPing(true), 0);
      const t1 = setTimeout(() => setHoneyPing(false), 3000);
      return () => {
        clearTimeout(t0);
        clearTimeout(t1);
      };
    }
    return undefined;
  }, [prediction?.honey_files]);

  return (
    <div className="h-full flex flex-col">
      <div className="h-10 bg-[#161b22] border border-gray-800 rounded-t-xl px-4 flex items-center gap-3">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-red-500/80" />
          <span className="h-2.5 w-2.5 rounded-full bg-yellow-500/80" />
          <span className="h-2.5 w-2.5 rounded-full bg-green-500/80" />
        </div>
        <div className="text-xs text-gray-300 font-mono flex-1">root@fintech-prod-01:~$</div>
        <div className="text-[10px] text-gray-500 font-mono">{shortId(sessionId)}</div>
      </div>

      <div className="flex-1 bg-black border-x border-b border-gray-800 rounded-b-xl overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto px-4 py-3 font-mono text-sm">
          {commands.length === 0 ? (
            <div className="text-gray-500">
              <div className="inline-flex items-center gap-2">
                <span className="text-cyan-400">█</span>
                <span className="animate-pulse">Waiting for attacker connection...</span>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {commands.map((c, idx) => {
                const isFlash = idx === flashIdx;
                return (
                  <div
                    key={`${c.timestamp || idx}-${idx}`}
                    className={isFlash ? "bg-cyan-500/10 ring-1 ring-cyan-500/30 rounded-md p-2 -m-2 transition" : ""}
                  >
                    <div className="text-xs text-gray-500">
                      {fmtTs(c.timestamp)} <span className="text-gray-700">|</span>{" "}
                      <span className="text-cyan-300">{c.command}</span>{" "}
                      <span className={["ml-2", stageColor(c.stage)].join(" ")}>[{String(c.stage || "unknown")}]</span>
                    </div>
                    <pre className="whitespace-pre-wrap text-gray-300 mt-1 leading-relaxed">{c.response}</pre>
                    <div className="h-1" />
                  </div>
                );
              })}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        <div className="border-t border-gray-800 bg-[#0d1117] px-4 py-3">
          <div className="text-xs tracking-widest text-gray-300 font-semibold">MITRE ATT&CK PREDICTION</div>

          <div className="mt-2 flex items-center gap-3 flex-wrap">
            <div className="text-sm text-gray-200 font-mono">
              <span className={stageColor(stage)}>{String(prediction?.current_stage || "unknown")}</span>{" "}
              <span className="text-gray-500">→</span>{" "}
              <span className="text-cyan-200">{String(prediction?.next_stage || "unknown")}</span>
            </div>

            <div className="flex-1 min-w-[160px]">
              <div className="h-2 rounded-full bg-gray-900 border border-gray-800 overflow-hidden">
                <div
                  className="h-full bg-cyan-500 transition-all duration-500"
                  style={{ width: confidencePct }}
                />
              </div>
              <div className="mt-1 text-[10px] text-gray-500 font-mono">CONFIDENCE {confidencePct}</div>
            </div>
          </div>

          <div className="mt-2 flex flex-wrap gap-2">
            {(prediction?.technique_tags || []).slice(0, 10).map((t) => (
              <span
                key={t}
                className="text-[10px] px-2 py-0.5 rounded-full bg-[#161b22] border border-gray-800 text-gray-200"
              >
                {t}
              </span>
            ))}
            {(prediction?.technique_tags || []).length === 0 ? (
              <span className="text-[10px] text-gray-500">No techniques detected yet.</span>
            ) : null}
          </div>

          {honeyPing ? (
            <div className="mt-3 text-xs text-cyan-200 font-semibold">
              🪤 HONEY FILE PLANTED
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

