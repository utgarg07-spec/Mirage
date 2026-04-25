import { useEffect, useMemo, useState } from "react";

import useWebSocket from "../hooks/useWebSocket";
import Navbar from "../components/Navbar";

function shortHash(h) {
  const s = String(h || "");
  if (!s) return "—";
  if (s.length <= 18) return s;
  return `${s.slice(0, 8)}...${s.slice(-6)}`;
}

function fmtUtc(iso) {
  try {
    const d = new Date(iso);
    return `${String(d.getUTCHours()).padStart(2, "0")}:${String(d.getUTCMinutes()).padStart(2, "0")}:${String(
      d.getUTCSeconds(),
    ).padStart(2, "0")} UTC`;
  } catch {
    return "—";
  }
}

export default function NodeTwo() {
  const { networkAlert, blockchainFeed, isConnected } = useWebSocket();
  const [phase, setPhase] = useState("idle"); // idle | p1 | p2 | p3

  useEffect(() => {
    if (!networkAlert) {
      const t0 = setTimeout(() => setPhase("idle"), 0);
      return () => clearTimeout(t0);
    }
    const t0 = setTimeout(() => setPhase("p1"), 0);
    const t2 = setTimeout(() => setPhase("p2"), 1500);
    const t3 = setTimeout(() => setPhase("p3"), 3500);
    return () => {
      clearTimeout(t0);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [networkAlert]);

  const card = useMemo(() => {
    if (!networkAlert || phase === "idle") {
      return {
        bg: "bg-[#161b22] border-gray-800",
        title: "fintech-backup-01",
        status: "STATUS: MONITORING",
        sub: "No threats received",
        badge: "MONITORING",
        badgeCls: "bg-gray-500/15 border-gray-800 text-gray-200",
      };
    }

    if (phase === "p1") {
      return {
        bg: "bg-red-950/30 border-red-700 animate-pulse",
        title: "fintech-backup-01",
        status: "⚠ THREAT FINGERPRINT INCOMING",
        sub: "Signal received from Node-1",
        badge: "ALERT",
        badgeCls: "bg-red-500/15 border-red-800 text-red-200",
      };
    }

    if (phase === "p2") {
      return {
        bg: "bg-yellow-950/20 border-yellow-700",
        title: "fintech-backup-01",
        status: "VERIFYING ON BLOCKCHAIN...",
        sub: "Synchronizing fingerprint + validating ledger",
        badge: "SYNC",
        badgeCls: "bg-yellow-500/15 border-yellow-800 text-yellow-200",
      };
    }

    return {
      bg: "bg-green-950/25 border-green-700 shadow-[0_0_50px_rgba(34,197,94,0.18)]",
      title: "fintech-backup-01",
      status: "✓ SYSTEM IMMUNIZED",
      sub: "Attacker pre-blocked based on Node-1 intelligence",
      badge: "BLOCKCHAIN VERIFIED",
      badgeCls: "bg-green-500/15 border-green-800 text-green-200",
    };
  }, [networkAlert, phase]);

  const feed = useMemo(() => (Array.isArray(blockchainFeed) ? blockchainFeed.slice(0, 12) : []), [blockchainFeed]);

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white flex flex-col">
      <Navbar isConnected={isConnected} blockchainCount={feed.length} centerLabel="COMMAND CENTER — NODE 2" />

      <div className="flex-1 px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <div className={["rounded-2xl border p-10 transition-all duration-700", card.bg].join(" ")}>
            <div className="flex items-center justify-between gap-4">
              <div>
                <div className="text-gray-300 tracking-widest text-xs font-semibold">NODE 2</div>
                <div className="text-3xl font-mono mt-2">{card.title}</div>
              </div>
              <div className={["text-[10px] px-3 py-1 rounded-full border font-semibold tracking-widest", card.badgeCls].join(" ")}>
                {card.badge}
              </div>
            </div>

            <div className="mt-8 text-2xl font-semibold">{card.status}</div>
            <div className="mt-2 text-gray-300">{card.sub}</div>

            <div className="mt-6 grid grid-cols-2 gap-4">
              <div className="rounded-xl bg-black/20 border border-gray-800 p-4">
                <div className="text-xs text-gray-400 tracking-widest">FINGERPRINT</div>
                <div className="mt-2 text-cyan-200 font-mono text-lg">{shortHash(networkAlert?.fingerprint)}</div>
              </div>
              <div className="rounded-xl bg-black/20 border border-gray-800 p-4">
                <div className="text-xs text-gray-400 tracking-widest">TX HASH</div>
                <div className="mt-2 text-gray-200 font-mono text-lg">{shortHash(networkAlert?.tx_hash)}</div>
              </div>
            </div>
          </div>

          <div className="mt-6 rounded-xl bg-[#161b22] border border-gray-800 p-4">
            <div className="flex items-center justify-between">
              <div className="text-xs tracking-widest text-gray-300 font-semibold">THREAT INTELLIGENCE FEED</div>
              <div className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-950/20 border border-cyan-900 text-cyan-200 font-semibold">
                AUTO-BLOCKED
              </div>
            </div>

            <div className="mt-3 overflow-y-auto max-h-[280px] space-y-2">
              {feed.length === 0 ? (
                <div className="text-sm text-gray-500">No ledger activity yet.</div>
              ) : (
                feed.map((it, idx) => (
                  <div key={`${it.fingerprint || idx}-${idx}`} className="rounded-lg border border-gray-800 bg-black/20 p-3">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-xs text-gray-200 font-mono">{shortHash(it.fingerprint)}</div>
                      <div className="text-[10px] text-gray-500 font-mono">{fmtUtc(it.timestamp)}</div>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-2">
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-black/25 border border-gray-800 text-gray-200">
                        {String(it.stage || "unknown").replaceAll("_", " ")}
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-black/25 border border-gray-800 text-gray-200">
                        SKILL {Number(it.skill_level || 1)}
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-950/15 border border-cyan-900 text-cyan-200 font-semibold">
                        AUTO-BLOCKED
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

