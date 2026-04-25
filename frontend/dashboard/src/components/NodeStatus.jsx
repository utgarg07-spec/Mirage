import { useEffect, useMemo, useState } from "react";

function shortHash(h) {
  const s = String(h || "");
  if (!s) return "—";
  if (s.length <= 18) return s;
  return `${s.slice(0, 8)}...${s.slice(-6)}`;
}

export default function NodeStatus({ networkAlert, activeCount = 0 }) {
  const [phase, setPhase] = useState("idle"); // idle | red | yellow | green

  useEffect(() => {
    if (!networkAlert) {
      const t0 = setTimeout(() => setPhase("idle"), 0);
      return () => clearTimeout(t0);
    }

    const t0 = setTimeout(() => setPhase("red"), 0);
    const t1 = setTimeout(() => setPhase("yellow"), 1000);
    const t2 = setTimeout(() => setPhase("green"), 3000);
    const t3 = setTimeout(() => setPhase("idle"), 5000);
    return () => {
      clearTimeout(t0);
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [networkAlert]);

  const node2 = useMemo(() => {
    if (!networkAlert) {
      return {
        header: "fintech-backup-01",
        status: "MONITORING",
        cls: "border-gray-800 bg-black/15 text-gray-300",
        sub: "No threats received",
      };
    }

    if (phase === "red") {
      return {
        header: "fintech-backup-01",
        status: "⚠ THREAT DETECTED",
        cls: "border-red-700 bg-red-950/30 text-red-200 animate-pulse",
        sub: "Inbound fingerprint signal",
      };
    }

    if (phase === "yellow") {
      return {
        header: "fintech-backup-01",
        status: "⟳ SYNCING FINGERPRINT...",
        cls: "border-yellow-700 bg-yellow-950/20 text-yellow-200",
        sub: "Verifying on-chain immunity",
      };
    }

    if (phase === "green") {
      return {
        header: "fintech-backup-01",
        status: "✓ IMMUNIZED",
        cls: "border-green-700 bg-green-950/25 text-green-200 shadow-[0_0_30px_rgba(34,197,94,0.18)] animate-pulse",
        sub: "Threat pre-blocked by Node-1 intelligence",
      };
    }

    return {
      header: "fintech-backup-01",
      status: "MONITORING",
      cls: "border-gray-800 bg-black/15 text-gray-300",
      sub: "No threats received",
    };
  }, [networkAlert, phase]);

  return (
    <div className="rounded-xl bg-[#161b22] border border-gray-800 p-4">
      <div className="text-xs tracking-widest text-gray-300 font-semibold">NETWORK IMMUNITY</div>

      <div className="mt-3 space-y-3">
        <div className="rounded-xl border border-green-800 bg-green-950/15 p-3">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-100 font-mono">NODE 1</div>
            <div className="text-[10px] px-2 py-0.5 rounded-full border border-green-800 bg-green-950/20 text-green-200 font-semibold">
              PROTECTED — ACTIVE TRAP
            </div>
          </div>
          <div className="mt-2 text-xs text-gray-400">Active sessions</div>
          <div className="text-lg text-cyan-200 font-mono">{Number(activeCount || 0)}</div>
        </div>

        <div className={["rounded-xl border p-3 transition-all duration-500", node2.cls].join(" ")}>
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-100 font-mono">NODE 2</div>
            <div className="text-[10px] px-2 py-0.5 rounded-full border border-gray-800 bg-black/25 text-gray-200 font-semibold">
              {node2.status}
            </div>
          </div>
          <div className="mt-2 text-xs text-gray-400">{node2.header}</div>
          <div className="mt-1 text-xs text-gray-400">{node2.sub}</div>
          <div className="mt-2 text-xs font-mono text-gray-200">
            FP: <span className="text-cyan-200">{shortHash(networkAlert?.fingerprint)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

