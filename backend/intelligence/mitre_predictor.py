"""Simple ATT&CK stage predictor for attacker command streams."""

from __future__ import annotations


class MitrePredictor:
    STAGES = {
        "reconnaissance": {
            "keywords": ["nmap", "ping", "traceroute", "whois", "scan", "host"],
            "next": {"initial_access": 0.80, "execution": 0.20},
        },
        "initial_access": {
            "keywords": ["ssh", "login", "passwd", "password", "auth"],
            "next": {"execution": 0.70, "persistence": 0.30},
        },
        "execution": {
            "keywords": ["wget", "curl", "python", "bash", "chmod", "./", "perl", "ruby"],
            "next": {"privilege_escalation": 0.60, "collection": 0.40},
        },
        "privilege_escalation": {
            "keywords": ["sudo", "su ", "passwd", "shadow", "suid", "id", "uid=0"],
            "next": {"collection": 0.75, "exfiltration": 0.25},
        },
        "collection": {
            "keywords": ["cat", "find", "grep", "tar", "zip", "cp", "ls", "read"],
            "next": {"exfiltration": 0.85, "impact": 0.15},
        },
        "exfiltration": {
            "keywords": ["scp", "curl -x", "curl --data", "wget --post", "nc ", "netcat", "post"],
            "next": {"impact": 0.90, "complete": 0.10},
        },
        "impact": {
            "keywords": ["rm -rf", "shred", "dd ", "crontab", "systemctl", "mkfs"],
            "next": {"complete": 1.0},
        },
    }

    HONEY_FILES = {
        "reconnaissance": [],
        "initial_access": ["backup_credentials.txt"],
        "execution": ["deploy_keys.sh", "db_connection.py"],
        "privilege_escalation": ["sudo_config_backup.txt", "root_cron.sh"],
        "collection": ["accounts_master_2026.xlsx", "swift_codes.json"],
        "exfiltration": ["offshore_transfers_q1.csv", "kyc_dump_march.csv"],
        "impact": [],
    }

    TECHNIQUE_TAGS = {
        "reconnaissance": ["T1595 - Active Scanning", "T1046 - Network Service Discovery"],
        "initial_access": ["T1078 - Valid Accounts", "T1110 - Brute Force"],
        "execution": ["T1059 - Command and Scripting Interpreter"],
        "privilege_escalation": [
            "T1548 - Abuse Elevation Control",
            "T1068 - Exploitation for Privilege Escalation",
        ],
        "collection": ["T1005 - Data from Local System", "T1083 - File and Directory Discovery"],
        "exfiltration": [
            "T1041 - Exfiltration Over C2 Channel",
            "T1048 - Exfiltration Over Alternative Protocol",
        ],
        "impact": ["T1485 - Data Destruction", "T1486 - Data Encrypted for Impact"],
    }

    STAGE_ORDER = [
        "reconnaissance",
        "initial_access",
        "execution",
        "privilege_escalation",
        "collection",
        "exfiltration",
        "impact",
    ]

    def predict(self, commands: list[str]) -> dict:
        if not commands:
            return {
                "current_stage": "reconnaissance",
                "next_stage": "initial_access",
                "confidence": 0.0,
                "honey_files": self.HONEY_FILES["reconnaissance"],
                "skill_level": 1,
                "technique_tags": self.TECHNIQUE_TAGS["reconnaissance"],
            }

        total = len(commands)
        scores = {stage: 0.0 for stage in self.STAGES}
        weighted_hits = 0.0

        for index, command in enumerate(commands, start=1):
            lowered_command = command.lower()
            weight = index / total
            for stage, data in self.STAGES.items():
                if any(keyword.lower() in lowered_command for keyword in data["keywords"]):
                    scores[stage] += weight
                    weighted_hits += weight

        best_stage = max(scores, key=scores.get)
        best_score = scores[best_stage]
        confidence = 0.0 if weighted_hits == 0 else min(1.0, best_score / weighted_hits)

        next_stage_probs = self.STAGES[best_stage]["next"]
        next_stage = max(next_stage_probs, key=next_stage_probs.get) if next_stage_probs else "complete"

        reached_index = max(
            (idx for idx, stage in enumerate(self.STAGE_ORDER) if scores[stage] > 0),
            default=0,
        )
        if reached_index <= 1:
            skill_level = 1
        elif reached_index <= 3:
            skill_level = 2
        else:
            skill_level = 3

        return {
            "current_stage": best_stage,
            "next_stage": next_stage,
            "confidence": round(confidence, 2),
            "honey_files": list(self.HONEY_FILES.get(best_stage, [])),
            "skill_level": skill_level,
            "technique_tags": list(self.TECHNIQUE_TAGS.get(best_stage, [])),
        }
