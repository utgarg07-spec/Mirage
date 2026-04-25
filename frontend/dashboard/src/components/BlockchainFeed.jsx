import { useMemo } from "react";

function shortHash(h) {
  const s = String(h || "");
  if (s.length <= 18) return s || "—";
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

function stageLabel(stage) {
  return String(stage || "unknown").replaceAll("_", " ");
}

export default function BlockchainFeed({ blockchainFeed, threatCount }) {
  const items = useMemo(() => (Array.isArray(blockchainFeed) ? blockchainFeed.slice(0, 5) : []), [blockchainFeed]);

  return (
    <div className="rounded-xl bg-[#161b22] border border-gray-800 p-4 flex flex-col">
      <div className="flex items-center justify-between">
        <div className="text-xs tracking-widest text-gray-300 font-semibold">BLOCKCHAIN LEDGER</div>
        <div className="text-[10px] px-2 py-0.5 rounded-full bg-green-950/20 border border-green-900 text-green-200 font-semibold">
          ✓ ON-CHAIN
        </div>
      </div>

      <div className="mt-3 flex-1 overflow-y-auto space-y-2">
        {items.length === 0 ? (
          <div className="text-sm text-gray-500">No threat registrations yet.</div>
        ) : (
          items.map((it, idx) => (
            <div
              key={`${it.fingerprint || it.tx_hash || idx}-${idx}`}
              className={[
                "rounded-lg border border-cyan-900/40 bg-cyan-950/10 p-3 transition",
                idx === 0 ? "shadow-[0_0_22px_rgba(34,211,238,0.25)]" : "",
              ].join(" ")}
            >
              <div className="flex items-center justify-between gap-3">
                <div className="text-xs text-gray-200 font-mono">{shortHash(it.fingerprint)}</div>
                <div className="text-[10px] text-gray-500 font-mono">{fmtUtc(it.timestamp)}</div>
              </div>
              <div className="mt-2 flex items-center gap-2 flex-wrap">
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-black/25 border border-gray-800 text-gray-200">
                  SKILL {Number(it.skill_level || 1)}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-black/25 border border-gray-800 text-gray-200">
                  {stageLabel(it.stage)}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="mt-3 pt-3 border-t border-gray-800 text-xs text-gray-300 flex items-center justify-between">
        <div className="tracking-widest">TOTAL THREATS REGISTERED</div>
        <div className="font-mono text-cyan-200">{Number(threatCount || 0)}</div>
      </div>
    </div>
  );
}

