import { useEffect, useMemo, useState } from "react";

function formatUtcTime(d) {
  const hh = String(d.getUTCHours()).padStart(2, "0");
  const mm = String(d.getUTCMinutes()).padStart(2, "0");
  const ss = String(d.getUTCSeconds()).padStart(2, "0");
  return `${hh}:${mm}:${ss} UTC`;
}

export default function Navbar({ isConnected, blockchainCount, centerLabel = "COMMAND CENTER — NODE 1" }) {
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const timeText = useMemo(() => formatUtcTime(now), [now]);

  return (
    <div className="h-14 bg-[#0d1117] border-b border-cyan-900 flex items-center px-5">
      <div className="flex items-center gap-2">
        <div className="text-cyan-400 font-bold text-xl tracking-tight">◈ MIRAGE</div>
      </div>

      <div className="flex-1 text-center text-gray-400 text-sm tracking-widest">{centerLabel}</div>

      <div className="flex items-center gap-3">
        <div
          className={[
            "flex items-center gap-2 rounded-full px-3 py-1 border text-xs tracking-wider",
            isConnected
              ? "border-green-700 bg-green-950/30 text-green-300"
              : "border-red-800 bg-red-950/30 text-red-300",
          ].join(" ")}
        >
          <span
            className={[
              "h-2 w-2 rounded-full",
              isConnected ? "bg-green-400 animate-pulse" : "bg-red-400",
            ].join(" ")}
          />
          <span className="font-semibold">{isConnected ? "HONEYPOT ACTIVE" : "HONEYPOT OFFLINE"}</span>
        </div>

        <div className="flex items-center gap-2 rounded-full px-3 py-1 border border-cyan-900 bg-cyan-950/20 text-cyan-200 text-xs tracking-wider">
          <span className="h-2 w-2 rounded-full bg-cyan-400" />
          <span className="font-semibold">BLOCKCHAIN SYNCED</span>
          <span className="text-cyan-300/70">({Number(blockchainCount || 0)})</span>
        </div>

        <div className="rounded-full px-3 py-1 border border-gray-800 bg-[#161b22] text-gray-200 text-xs font-mono">
          {timeText}
        </div>
      </div>
    </div>
  );
}

