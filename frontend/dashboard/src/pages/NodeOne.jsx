import { useEffect, useMemo, useState } from "react";

import useWebSocket from "../hooks/useWebSocket";
import Navbar from "../components/Navbar";
import SessionList from "../components/SessionList";
import Terminal from "../components/Terminal";
import AttackerProfile from "../components/AttackerProfile";
import BlockchainFeed from "../components/BlockchainFeed";
import NodeStatus from "../components/NodeStatus";
import ForensicModal from "../components/ForensicModal";

const API_BASE = "http://localhost:8000";

async function fetchThreatCount() {
  const res = await fetch(`${API_BASE}/blockchain/threats/count`);
  if (!res.ok) return 0;
  const data = await res.json();
  return Number(data.count || 0);
}

export default function NodeOne() {
  const { sessions, activeSessionId, setActiveSessionId, liveCommands, predictions, blockchainFeed, networkAlert, isConnected } =
    useWebSocket();

  const [threatCount, setThreatCount] = useState(0);
  const [showForensics, setShowForensics] = useState(false);

  useEffect(() => {
    let alive = true;
    async function run() {
      const n = await fetchThreatCount();
      if (!alive) return;
      setThreatCount(n);
    }
    run();
    const t = setInterval(run, 5000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, []);

  const selectedSession = useMemo(() => sessions.find((s) => s.session_id === activeSessionId) || null, [sessions, activeSessionId]);

  const selectedCommands = useMemo(() => {
    if (!activeSessionId) return [];
    return liveCommands?.[activeSessionId] || [];
  }, [liveCommands, activeSessionId]);

  const selectedPrediction = useMemo(() => {
    if (!activeSessionId) return {};
    return predictions?.[activeSessionId] || {};
  }, [predictions, activeSessionId]);

  const sessionsWithCounts = useMemo(() => {
    const list = Array.isArray(sessions) ? sessions : [];
    return list.map((s) => ({
      ...s,
      command_count: (liveCommands?.[s.session_id] || []).length,
    }));
  }, [sessions, liveCommands]);

  const totalSessions = sessionsWithCounts.length;
  const activeCount = sessionsWithCounts.filter((s) => s.is_active).length;

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white flex flex-col">
      <Navbar isConnected={isConnected} blockchainCount={threatCount} centerLabel="COMMAND CENTER — NODE 1" />

      <div className="flex-1 grid grid-cols-12 gap-4 px-4 py-4 pb-16">
        <div className="col-span-3 h-[calc(100vh-56px-64px-32px)]">
          <div className="h-full rounded-xl bg-[#161b22] border border-gray-800 overflow-hidden">
            <SessionList
              sessions={sessionsWithCounts}
              predictions={predictions}
              activeSessionId={activeSessionId}
              setActiveSessionId={setActiveSessionId}
            />
          </div>
        </div>

        <div className="col-span-6 h-[calc(100vh-56px-64px-32px)]">
          <Terminal commands={selectedCommands} prediction={selectedPrediction} sessionId={activeSessionId} />
        </div>

        <div className="col-span-3 h-[calc(100vh-56px-64px-32px)] overflow-y-auto pr-1 space-y-4">
          <AttackerProfile session={selectedSession ? { ...selectedSession, command_count: selectedCommands.length } : null} prediction={selectedPrediction} />
          <BlockchainFeed blockchainFeed={blockchainFeed} threatCount={threatCount} />
          <NodeStatus networkAlert={networkAlert} activeCount={activeCount} />
        </div>
      </div>

      <div className="h-12 fixed bottom-0 left-0 right-0 bg-[#0d1117] border-t border-cyan-900 flex items-center justify-between px-5">
        <div className="text-xs text-gray-300 flex items-center gap-3 font-mono">
          <span>SESSIONS: {totalSessions}</span>
          <span className="text-gray-600">|</span>
          <span>ACTIVE: {activeCount}</span>
          <span className="text-gray-600">|</span>
          <span>THREATS ON-CHAIN: {threatCount}</span>
        </div>

        <button
          type="button"
          disabled={!activeSessionId}
          onClick={() => setShowForensics(true)}
          className={[
            "px-4 py-2 rounded-lg font-semibold transition",
            activeSessionId ? "bg-cyan-500 text-black hover:bg-cyan-400" : "bg-gray-800 text-gray-500 cursor-not-allowed",
          ].join(" ")}
        >
          GENERATE FORENSIC BRIEF
        </button>
      </div>

      {showForensics && activeSessionId ? (
        <ForensicModal sessionId={activeSessionId} onClose={() => setShowForensics(false)} />
      ) : null}
    </div>
  );
}

